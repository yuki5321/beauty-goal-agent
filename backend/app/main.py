import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.agent.orchestrator import agent_orchestrator
from app.governance.memory_pipe import memory_pipe

app = FastAPI(
    title="Beauty Goal Agent API",
    description="自律型メイク・スタイリング最適化エージェント API (OODA Loop & YouCam MCP / Gemini)",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Beauty Goal Agent Core",
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "youcam_configured": bool(settings.YOUCAM_API_KEY),
        "use_mock_youcam": settings.USE_MOCK_YOUCAM or not bool(settings.YOUCAM_API_KEY)
    }

@app.post("/api/agent/optimize")
async def optimize_beauty_goal(
    goal: str = Form("midface_shortening"),
    image: UploadFile = File(...)
):
    """
    顔画像と目標（Goal）を受け取り、OODA試行錯誤ループをSSE形式でリアルタイム配信する。
    生体画像データはRAMメモリ上でのみ処理され、ディスク・DBへの保存は行われません。
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="有効な画像ファイルをアップロードしてください。")

    image_bytes = await image.read()
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    event_generator = agent_orchestrator.run_optimization_loop(
        session_id=session_id,
        goal=goal,
        image_bytes=image_bytes
    )

    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/agent/feedback-replan")
async def feedback_replan_endpoint(
    session_id: str = Form(...),
    goal: str = Form("midface_shortening"),
    current_plan_json: str = Form(...),
    user_feedback: str = Form(...),
    image: UploadFile = File(None)
):
    """
    ユーザーからの自然言語追加フィードバックを受け取り、協調型Replan（Human-in-the-Loop）を実行するSSEエンドポイント
    """
    import json
    try:
        current_plan = json.loads(current_plan_json)
    except Exception:
        current_plan = {}

    fallback_bytes = None
    if image:
        fallback_bytes = await image.read()

    event_generator = agent_orchestrator.run_feedback_replan(
        session_id=session_id,
        goal=goal,
        current_plan=current_plan,
        user_feedback=user_feedback,
        fallback_image_bytes=fallback_bytes
    )

    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/session/purge/{session_id}")
async def purge_session(session_id: str):
    """N-G03: セッション終了時にメモリから生体顔画像データを即時破棄"""
    memory_pipe.purge_session(session_id)
    return {"status": "SUCCESS", "message": f"Session {session_id} memory purged."}

# フロントエンド静的配信 (Cloud Run / 本番用)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
