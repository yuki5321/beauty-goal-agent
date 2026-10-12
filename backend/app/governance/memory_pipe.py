import asyncio
import gc
import io
import time
from typing import Any, Dict, Optional

class SessionMemoryPipe:
    """
    N-G03: 生体顔写真のデータ最小化と即時破棄。
    アップロードされた顔画像はCloud RunのRAM（メモリ）上でのみ処理し、
    ファイルシステムやDBへの永続保存を禁止する。
    セッション完了またはタイムアウト時にメモリ変数を強制消去（ゼロフィル/GC）する。
    """
    def __init__(self, ttl_seconds: int = 300):
        # session_id -> {"image_bytes": bytes, "timestamp": float, "content_type": str}
        self._storage: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def store_image(self, session_id: str, image_bytes: bytes, content_type: str = "image/jpeg") -> None:
        self._cleanup_expired()
        self._storage[session_id] = {
            "image_bytes": image_bytes,
            "timestamp": time.time(),
            "content_type": content_type
        }

    def get_image(self, session_id: str) -> Optional[bytes]:
        self._cleanup_expired()
        data = self._storage.get(session_id)
        if not data:
            return None
        return data["image_bytes"]

    def purge_session(self, session_id: str) -> None:
        if session_id in self._storage:
            del self._storage[session_id]
            gc.collect()

    def active_session_count(self) -> int:
        return len(self._storage)

    async def run_ttl_sweeper(self, interval_seconds: int = 30) -> None:
        """新規アクセスが無くてもTTL超過画像を定期破棄するバックグラウンドタスク"""
        while True:
            await asyncio.sleep(interval_seconds)
            self._cleanup_expired()

    def _cleanup_expired(self) -> None:
        now = time.time()
        expired = [sid for sid, item in self._storage.items() if now - item["timestamp"] > self.ttl_seconds]
        for sid in expired:
            del self._storage[sid]
        if expired:
            gc.collect()

# シングルトンインスタンス
memory_pipe = SessionMemoryPipe()
