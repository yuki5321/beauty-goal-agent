import pytest
from app.governance.guardrail import SafetyGuardrail
from app.governance.memory_pipe import SessionMemoryPipe
from app.agent.proportion import ProportionAnalyzer

def test_lookism_guardrail_blocks_offensive_words():
    # 容姿批判用語のブロック確認
    safe, msg = SafetyGuardrail.inspect_text_input("ブサイクな顔を直したい")
    assert not safe
    assert "倫理規程" in msg

    # 点数化・欠点表現のブロック確認
    safe, msg = SafetyGuardrail.inspect_text_input("顔の欠点を60点から改善したい")
    assert not safe

    # 適切な目標表現はパス
    safe, msg = SafetyGuardrail.inspect_text_input("中顔面短縮")
    assert safe

def test_bone_deformation_guardrail_blocks_physical_reshape():
    # 物理的骨格変形ツールの遮断確認
    safe, msg = SafetyGuardrail.inspect_tool_call("AI_Face_Reshape", {})
    assert not safe
    assert "ディスモルフィア抑止" in msg

    # 過剰なオーバーリップの遮断確認 (最大1.3倍まで)
    safe, msg = SafetyGuardrail.inspect_tool_call("simulate_makeup", {"lip_over_ratio": 1.5})
    assert not safe
    assert "安全リミット違反" in msg

    # 正常なメイクツールの許可
    safe, msg = SafetyGuardrail.inspect_tool_call("simulate_makeup", {"lip_over_ratio": 1.15})
    assert safe

def test_proportion_calculation():
    landmarks = {
        "hairline_y": 100.0,
        "eye_center_y": 200.0,
        "upper_lip_y": 340.0,
        "chin_y": 500.0
    }
    # H_mid = 140, H_total = 400 => ratio = 140 / 400 = 0.35
    ratio = ProportionAnalyzer.calculate_midface_ratio(landmarks)
    assert ratio == 0.35

    # 目標スコアの計算
    score = ProportionAnalyzer.calculate_goal_score("midface_shortening", 0.31)
    assert score == 100  # 理想比率で満点

    score_sub = ProportionAnalyzer.calculate_goal_score("midface_shortening", 0.35)
    assert 60 <= score_sub <= 75

def test_biometric_memory_pipeline():
    pipe = SessionMemoryPipe(ttl_seconds=10)
    fake_bytes = b"fake_biometric_face_data"
    sid = "test_session_123"

    pipe.store_image(sid, fake_bytes)
    assert pipe.get_image(sid) == fake_bytes

    # 即時破棄の確認
    pipe.purge_session(sid)
    assert pipe.get_image(sid) is None

@pytest.mark.anyio
async def test_feedback_replan_execution():
    from app.agent.orchestrator import agent_orchestrator
    from PIL import Image
    import io

    img = Image.new("RGB", (200, 200), color=(250, 220, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    sid = "test_feedback_session"
    current_plan = {
        "blush_placement": "horizontal_low",
        "blush_color": "#FF8C7A",
        "lip_over_ratio": 1.15,
        "eyeshadow_lower_intensity": 70.0,
        "bangs_style": "see_through"
    }

    events = []
    async for sse in agent_orchestrator.run_feedback_replan(
        session_id=sid,
        goal="midface_shortening",
        current_plan=current_plan,
        user_feedback="リップを落ち着いた色にして前髪なしを試したい",
        fallback_image_bytes=img_bytes
    ):
        events.append(sse)

    assert len(events) > 0
    # final_result が含まれていること
    has_final = any('"type": "final_result"' in e for e in events)
    assert has_final


def test_lookism_guardrail_allows_neutral_words_containing_kanji():
    # 「点」「直」を含む通常の表現は誤検出しない
    for text in ["目元に焦点を当てたい", "唇の頂点を高く見せたい", "直線的な眉にしたい", "口が直線的に見える"]:
        safe, _ = SafetyGuardrail.inspect_text_input(text)
        assert safe, text

    # 文脈付きの採点・矯正表現はブロック
    for text in ["今は60点くらい", "鼻を直したい", "顔が直せるメイク", "スコアを上げたい"]:
        safe, _ = SafetyGuardrail.inspect_text_input(text)
        assert not safe, text

def test_biometric_memory_pipeline_expires_other_sessions_on_access():
    pipe = SessionMemoryPipe(ttl_seconds=10)
    pipe.store_image("old", b"old_face")
    pipe._storage["old"]["timestamp"] -= 60
    pipe.store_image("new", b"new_face")

    # TTL超過セッションはアクセス時に一括破棄される
    assert pipe.get_image("new") == b"new_face"
    assert pipe.get_image("old") is None
    assert pipe.active_session_count() == 1

def _run_loop_events(ratio, monkeypatch):
    import asyncio, io, json
    from PIL import Image
    from app.agent.orchestrator import agent_orchestrator
    from app.mcp.client import youcam_client
    from app.agent import gemini

    async def fake_analyze(_bytes):
        return {"proportions": {"mid_face_ratio": ratio}}

    async def no_sleep(_s):
        return None

    monkeypatch.setattr(youcam_client, "analyze_face", fake_analyze)
    monkeypatch.setattr(gemini, "get_client", lambda: None)
    monkeypatch.setattr("app.agent.orchestrator.asyncio.sleep", no_sleep)

    buf = io.BytesIO()
    Image.new("RGB", (120, 120), (250, 220, 200)).save(buf, format="JPEG")

    async def collect():
        return [json.loads(e[len("data: "):]) async for e in
                agent_orchestrator.run_optimization_loop("session_test01", "midface_shortening", buf.getvalue())]
    return asyncio.run(collect())

def test_scores_depend_on_observed_ratio(monkeypatch):
    near = [e["score"] for e in _run_loop_events(0.355, monkeypatch) if e["type"] == "evaluation_result"]
    far = [e["score"] for e in _run_loop_events(0.42, monkeypatch) if e["type"] == "evaluation_result"]
    assert near[0] != far[0]
    assert near[-1] >= 85          # 標準的な比率は錯視調整で収束
    assert max(far) < 85           # 大きく離れた比率はサーキットブレーカーで終了

def test_circuit_breaker_reported_in_audit(monkeypatch):
    events = _run_loop_events(0.42, monkeypatch)
    types = [e["type"] for e in events]
    assert "circuit_breaker" in types and "converged" not in types
    final = next(e for e in events if e["type"] == "final_result")
    assert final["audit_certificate"]["agent_circuit_breaker"]["exit_status"].startswith("CIRCUIT_BREAKER")
    # 全プランが安全リミット内
    for e in events:
        if e["type"] == "evaluation_result":
            assert 1.0 <= e["plan"]["lip_over_ratio"] <= 1.3

def test_grounding_marks_only_products_found_in_search_answer():
    import asyncio
    from types import SimpleNamespace
    from app.agent.orchestrator import BeautyGoalOrchestrator
    from app.config import settings

    orch = BeautyGoalOrchestrator()
    plan = {"blush_placement": "horizontal_low", "lip_over_ratio": 1.1,
            "eyeshadow_lower_intensity": 50.0, "bangs_style": "see_through"}

    # APIキー未設定時は全商品が未検証
    if not settings.GEMINI_API_KEY:
        recipes = asyncio.run(orch._generate_makeup_recipe(plan))
        assert all(not p["grounding_verified"] for r in recipes for p in r["recommended_products"])

    recipes = [{"recommended_products": [
        {"brand": "KATE", "name": "リップモンスター", "grounding_verified": False},
        {"brand": "NARS", "name": "アフターグロー リキッドブラッシュ", "grounding_verified": False},
    ]}]
    res = SimpleNamespace(
        text="KATE リップモンスター 03 陽炎は現在も販売中です。",
        candidates=[SimpleNamespace(grounding_metadata=SimpleNamespace(grounding_chunks=[object()]))],
    )
    BeautyGoalOrchestrator._apply_grounding_result(recipes, res)
    flags = [p["grounding_verified"] for p in recipes[0]["recommended_products"]]
    assert flags == [True, False]


# ---- Gemini Planner (generate_json をモックしてキー無しで検証) ----

def _fake_gemini(monkeypatch, responses):
    """gemini.generate_json を、system_instruction ごとの応答で置き換える"""
    from app.agent import gemini
    from app.agent import prompts

    calls = []

    async def fake_generate_json(system_instruction, contents, temperature=0.3):
        calls.append(system_instruction)
        for key, value in responses.items():
            if system_instruction == getattr(prompts, key):
                return value
        return None

    monkeypatch.setattr(gemini, "get_client", lambda: object())
    monkeypatch.setattr(gemini, "generate_json", fake_generate_json)
    return calls

def test_planner_normalizes_llm_output():
    from app.agent.planner import _normalize_plan, INITIAL_PLAN

    raw = {
        "blush_placement": "under_eye_extreme",   # 不正なenum → base
        "blush_color": "red",                     # 不正な色 → base
        "lip_over_ratio": 1.6,                    # 上限1.3へ補正
        "eyeshadow_lower_intensity": "80",
        "bangs_style": "curtain",
        "jaw_slimming": 0.8,                      # 未知キーは除去
    }
    plan = _normalize_plan(raw, INITIAL_PLAN)
    assert plan == {
        "blush_placement": "horizontal_low",
        "blush_color": "#FF8C7A",
        "lip_over_ratio": 1.3,
        "eyeshadow_lower_intensity": 80.0,
        "bangs_style": "curtain",
    }
    assert _normalize_plan("not json", INITIAL_PLAN) is None

def test_planner_falls_back_to_rules_when_gemini_fails(monkeypatch):
    import asyncio
    from app.agent.planner import styling_planner, INITIAL_PLAN

    _fake_gemini(monkeypatch, {})  # すべての呼び出しで None

    initial = asyncio.run(styling_planner.plan_initial("midface_shortening", 0.357, 0.31))
    assert initial.source == "rule" and initial.plan == INITIAL_PLAN

    proposal = {"eyeshadow_lower_intensity": 55.0}
    replanned = asyncio.run(styling_planner.replan("midface_shortening", INITIAL_PLAN, 83, "fb", proposal))
    assert replanned.source == "rule" and replanned.plan["eyeshadow_lower_intensity"] == 55.0

    fb = asyncio.run(styling_planner.interpret_feedback("midface_shortening", INITIAL_PLAN, "前髪なしで"))
    assert fb.source == "rule" and fb.plan["bangs_style"] == "none"

def test_planner_replan_ignores_no_op_llm_output(monkeypatch):
    import asyncio
    from app.agent.planner import styling_planner, INITIAL_PLAN

    _fake_gemini(monkeypatch, {"REPLAN_SYSTEM_INSTRUCTION": {"adjusted_parameters": dict(INITIAL_PLAN)}})
    decision = asyncio.run(styling_planner.replan(
        "midface_shortening", INITIAL_PLAN, 83, "fb", {"eyeshadow_lower_intensity": 55.0}))
    # LLMが前回と同じプランを返したらCritic提案で前進する
    assert decision.source == "rule" and decision.plan["eyeshadow_lower_intensity"] == 55.0

def test_planner_replaces_lookist_llm_thought(monkeypatch):
    import asyncio
    from app.agent.planner import styling_planner, NEUTRAL_THOUGHT

    _fake_gemini(monkeypatch, {"PLANNER_SYSTEM_INSTRUCTION": {
        "thought_process": "顔の欠点を隠すためにチークを入れます。",
        "proposed_plan": {"lip_over_ratio": 1.1},
    }})
    decision = asyncio.run(styling_planner.plan_initial("midface_shortening", 0.357, 0.31))
    assert decision.source == "gemini"
    assert decision.thought == NEUTRAL_THOUGHT
    assert decision.plan["lip_over_ratio"] == 1.1

def test_feedback_replan_uses_gemini_interpretation(monkeypatch):
    import asyncio, io, json
    from PIL import Image
    from app.agent.orchestrator import agent_orchestrator

    async def no_sleep(_s):
        return None
    monkeypatch.setattr("app.agent.orchestrator.asyncio.sleep", no_sleep)
    calls = _fake_gemini(monkeypatch, {"INTERACTIVE_FEEDBACK_INSTRUCTION": {
        "feedback_reflection": "大人っぽさを優先し、チークを斜めに入れて血色感を控えめにしました。",
        "adjusted_parameters": {"blush_placement": "diagonal_temple", "blush_color": "#C8786E", "lip_over_ratio": 1.05},
    }})

    buf = io.BytesIO()
    Image.new("RGB", (120, 120), (250, 220, 200)).save(buf, format="JPEG")
    plan = {"blush_placement": "horizontal_low", "blush_color": "#FF8C7A",
            "lip_over_ratio": 1.10, "eyeshadow_lower_intensity": 55.0, "bangs_style": "see_through"}

    async def collect():
        return [json.loads(e[len("data: "):]) async for e in agent_orchestrator.run_feedback_replan(
            session_id="session_fb_gemini", goal="midface_shortening", current_plan=plan,
            user_feedback="もう少し大人っぽい雰囲気にしたい", fallback_image_bytes=buf.getvalue())]
    events = asyncio.run(collect())

    from app.agent import prompts
    assert prompts.INTERACTIVE_FEEDBACK_INSTRUCTION in calls
    decide = next(e for e in events if e.get("step_name") == "DECIDE")
    assert decide["action"] == "gemini.plan_custom_interactive_parameters()"
    assert "大人っぽさ" in decide["thought"]
    final = next(e for e in events if e["type"] == "final_result")
    assert final["plan"]["blush_placement"] == "diagonal_temple"
    assert final["plan"]["blush_color"] == "#C8786E"
    assert final["plan"]["eyeshadow_lower_intensity"] == 55.0  # 指定外のキーは現状維持


# ---- YouCam API クライアント (httpx.MockTransport で実APIの応答を再現) ----

def _jpeg_bytes(size=(400, 500)):
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", size, (240, 210, 190)).save(buf, format="PNG")  # PNGでも内部でJPEG化される
    return buf.getvalue()

def _youcam_transport(task_results, calls, poll_statuses=("running", "success"), error=None):
    import httpx
    polls = {"n": 0}

    def handler(request: httpx.Request):
        path = request.url.path
        calls.append((request.method, path))
        if request.method == "POST" and path == "/s2s/v2.0/file":
            assert request.headers["Authorization"] == "Bearer test-key"
            return httpx.Response(200, json={"status": 200, "data": {"files": [{
                "file_id": "fid-1", "content_type": "image/jpeg", "file_name": "face.jpg",
                "requests": [{"url": "https://upload.example.com/put", "method": "PUT",
                              "headers": {"Content-Type": "image/jpeg", "Content-Length": 1}}]}]}})
        if request.method == "PUT" and request.url.host == "upload.example.com":
            assert request.content[:2] == b"\xff\xd8"  # JPEG
            return httpx.Response(200)
        if request.method == "POST" and path.startswith("/s2s/v2.0/task/"):
            assert request.read() and b"fid-1" in request.content
            return httpx.Response(200, json={"status": 200, "data": {"task_id": "t-1"}})
        if request.method == "GET" and path.startswith("/s2s/v2.0/task/"):
            feature = path.split("/")[4]
            status = poll_statuses[min(polls["n"], len(poll_statuses) - 1)]
            polls["n"] += 1
            data = {"task_status": status}
            if status == "success":
                data["results"] = task_results[feature]
            if status == "error":
                data.update({"error": error, "error_message": "detail"})
            return httpx.Response(200, json={"status": 200, "data": data})
        if request.method == "GET" and request.url.host == "result.example.com":
            assert "Authorization" not in request.headers
            return httpx.Response(200, content=b"RESULT-IMAGE")
        return httpx.Response(404)

    return httpx.MockTransport(handler)

def _youcam_client(transport, poll_timeout=5.0):
    from app.mcp.client import YouCamMCPClient
    from app.mcp.youcam_api import YouCamAPI
    api = YouCamAPI("https://yce-api-01.makeupar.com", "test-key", poll_interval=0, poll_timeout=poll_timeout, transport=transport)
    client = YouCamMCPClient(api=api)
    client.use_mock = False
    return client

def test_youcam_makeup_flow_returns_result_image():
    import asyncio
    calls = []
    client = _youcam_client(_youcam_transport({"makeup-vto": {"url": "https://result.example.com/r.jpg"}}, calls))
    plan = {"blush_placement": "horizontal_low", "blush_color": "#FF8C7A", "lip_over_ratio": 1.1,
            "eyeshadow_lower_intensity": 55.0, "bangs_style": "see_through"}

    result = asyncio.run(client.simulate_makeup_and_hair(_jpeg_bytes(), plan))
    assert result.source == "youcam" and result.image_bytes == b"RESULT-IMAGE"
    assert result.bangs_rendered is False and result.fallback_reason is None
    methods = [m for m, _ in calls]
    assert methods[:3] == ["POST", "PUT", "POST"] and methods.count("GET") >= 2

    # 同じ画像の2回目はアップロードを再利用
    calls.clear()
    asyncio.run(client.simulate_makeup_and_hair(_jpeg_bytes(), plan))
    assert ("POST", "/s2s/v2.0/file") not in calls

def test_youcam_task_error_falls_back_to_simulator():
    import asyncio
    calls = []
    client = _youcam_client(_youcam_transport({}, calls, poll_statuses=("error",), error="error_face_position_invalid"))
    result = asyncio.run(client.simulate_makeup_and_hair(_jpeg_bytes(), {"lip_over_ratio": 1.1}))
    assert result.source == "simulator"
    assert result.fallback_reason == "error_face_position_invalid"
    assert result.image_bytes[:2] == b"\xff\xd8"

def test_youcam_poll_timeout_falls_back():
    import asyncio
    client = _youcam_client(_youcam_transport({}, [], poll_statuses=("running",)), poll_timeout=0)
    result = asyncio.run(client.simulate_makeup_and_hair(_jpeg_bytes(), {}))
    assert result.source == "simulator" and result.fallback_reason == "poll_timeout"

def test_youcam_face_analysis_uses_horizontal_third_and_caches():
    import asyncio
    calls = []
    client = _youcam_client(_youcam_transport(
        {"face-attr-analysis": {"facialratio": {"horizontal_third": [30, 36, 34]}}}, calls))
    image = _jpeg_bytes()
    first = asyncio.run(client.analyze_face(image))
    assert first["source"] == "youcam"
    assert first["proportions"]["mid_face_ratio"] == 0.36
    n = len(calls)
    second = asyncio.run(client.analyze_face(image))
    assert second == first and len(calls) == n  # 10ユニット消費を避けるためキャッシュ

    client.forget(image)
    asyncio.run(client.analyze_face(image))
    assert len(calls) > n

def test_youcam_effects_mapping_is_within_limits():
    from app.mcp.youcam_mapping import plan_to_effects, LIP_LINER_NATURAL, LIP_LINER_OVER_UPPER

    def numbers(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from numbers(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from numbers(v)
        elif isinstance(obj, (int, float)):
            yield obj

    for lip, under_eye in [(1.0, 0.0), (1.18, 85.0), (1.3, 100.0)]:
        effects = plan_to_effects({"blush_placement": "apple_high", "lip_over_ratio": lip,
                                   "eyeshadow_lower_intensity": under_eye})
        assert all(0 <= n <= 100 for n in numbers(effects))
        liner = next(e for e in effects if e["category"] == "lip_liner")
        assert liner["pattern"]["name"] == (LIP_LINER_OVER_UPPER if lip > 1.0 else LIP_LINER_NATURAL)
        lip_color = next(e for e in effects if e["category"] == "lip_color")
        assert "morphology" not in lip_color  # N-G02: 唇の形状変形は使わない
        assert any(e["category"] == "concealer" for e in effects) == (under_eye > 0)
