import asyncio
import json
from typing import Any, List, Optional
from app.config import settings
from app.observability.logger import agent_logger

_client = None
_client_initialized = False


def get_client():
    """Gemini クライアントを遅延生成して共有する（APIキー未設定・SDK未導入時は None）"""
    global _client, _client_initialized
    if not _client_initialized:
        _client_initialized = True
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                _client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                agent_logger.info(f"Gemini client init failed, using rule-based fallbacks: {e}")
                _client = None
    return _client


def is_available() -> bool:
    return get_client() is not None


async def generate_json(system_instruction: str, contents: List[Any], temperature: float = 0.3) -> Optional[Any]:
    """
    JSONモードで Gemini を呼び出し、パース済みの結果を返す。
    同期SDKはスレッドで実行してイベントループを止めない。失敗時は None。
    """
    client = get_client()
    if client is None:
        return None

    def _call():
        from google.genai import types
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=temperature
            )
        )
        return json.loads(response.text) if response.text else None

    try:
        return await asyncio.to_thread(_call)
    except Exception as e:
        agent_logger.info(f"Gemini call failed: {e}")
        return None
