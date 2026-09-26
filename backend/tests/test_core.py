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
