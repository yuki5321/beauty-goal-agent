"""
YouCam API (Perfect Corp, https://yce-api-01.makeupar.com) の非同期タスククライアント。

流れ: POST /s2s/v2.0/file → 返却URLへ画像をPUT → POST /s2s/v2.0/task/<feature>
      → GET /s2s/v2.0/task/<feature>/<task_id> を success/error までポーリング。
タスクは成功した時点でユニットが消費されるため、開始したタスクはタイムアウトまでポーリングを続ける。
"""
import asyncio
import hashlib
import io
import time
from typing import Any, Dict, Optional, Tuple
import httpx
from PIL import Image
from app.mcp.youcam_mapping import plan_to_effects

MAX_LONG_SIDE = 1024
CACHE_TTL_SECONDS = 300


class YouCamError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code
        self.message = message


def prepare_image(image_bytes: bytes) -> bytes:
    """顔分析はJPEGのみ、試着は長辺1920px未満のため、RGB JPEG・長辺1024px以下に揃える"""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((MAX_LONG_SIDE, MAX_LONG_SIDE))
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=92)
        return out.getvalue()


class YouCamAPI:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        poll_interval: float = 1.5,
        poll_timeout: float = 90.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout
        self._transport = transport
        # 画像ハッシュ → (値, 保存時刻)。N-G03: TTLで破棄し、purge()で即時破棄できる
        self._file_ids: Dict[str, Tuple[str, float]] = {}
        self._face_results: Dict[str, Tuple[Dict[str, Any], float]] = {}

    # ---------- public ----------

    async def analyze_face(self, image_bytes: bytes) -> Dict[str, Any]:
        jpeg = prepare_image(image_bytes)
        key = self._hash(jpeg)
        cached = self._get_cached(self._face_results, key)
        if cached is not None:
            return cached

        async with self._client() as client:
            file_id = await self._upload(client, jpeg, key)
            results = await self._run_task(client, "face-attr-analysis", {
                "src_file_id": file_id,
                "features": ["horizontalThird"],
                "face_angle_strictness_level": "medium",
            })

        thirds = (results.get("facialratio") or {}).get("horizontal_third")
        if not isinstance(thirds, list) or len(thirds) != 3 or sum(thirds) <= 0:
            raise YouCamError("invalid_response", f"horizontal_third missing: {thirds!r}")
        total = float(sum(thirds))
        analysis = {
            "status": "SUCCESS",
            "source": "youcam",
            "horizontal_third": thirds,
            "proportions": {
                "upper_face_ratio": round(thirds[0] / total, 4),
                "mid_face_ratio": round(thirds[1] / total, 4),
                "lower_face_ratio": round(thirds[2] / total, 4),
            },
        }
        self._face_results[key] = (analysis, time.time())
        return analysis

    async def apply_makeup(self, image_bytes: bytes, plan: Dict[str, Any]) -> bytes:
        jpeg = prepare_image(image_bytes)
        key = self._hash(jpeg)
        async with self._client() as client:
            file_id = await self._upload(client, jpeg, key)
            results = await self._run_task(client, "makeup-vto", {
                "src_file_id": file_id,
                "version": "1.0",
                "effects": plan_to_effects(plan),
            })
            url = results.get("url")
            if not url:
                raise YouCamError("invalid_response", "results.url missing")
            # 結果URLは署名付きURLのため Authorization ヘッダを付けない
            res = await client.get(url)
            res.raise_for_status()
            return res.content

    def forget(self, image_bytes: bytes) -> None:
        """N-G03: セッション終了時に、その画像に紐づくfile_id・分析結果を破棄"""
        try:
            key = self._hash(prepare_image(image_bytes))
        except Exception:
            return
        self._file_ids.pop(key, None)
        self._face_results.pop(key, None)

    def purge(self) -> None:
        self._file_ids.clear()
        self._face_results.clear()

    # ---------- internals ----------

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=30.0, transport=self._transport)

    def _auth(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @staticmethod
    def _hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _get_cached(cache: Dict[str, Tuple[Any, float]], key: str) -> Any:
        now = time.time()
        for k in [k for k, (_, ts) in cache.items() if now - ts > CACHE_TTL_SECONDS]:
            del cache[k]
        entry = cache.get(key)
        return entry[0] if entry else None

    async def _upload(self, client: httpx.AsyncClient, jpeg: bytes, key: str) -> str:
        cached = self._get_cached(self._file_ids, key)
        if cached is not None:
            return cached

        res = await client.post(
            f"{self.base_url}/s2s/v2.0/file",
            headers=self._auth(),
            json={"files": [{"content_type": "image/jpeg", "file_name": "face.jpg", "file_size": len(jpeg)}]},
        )
        body = self._json_or_raise(res)
        try:
            file_info = body["data"]["files"][0]
            upload = file_info["requests"][0]
            file_id = file_info["file_id"]
        except (KeyError, IndexError, TypeError):
            raise YouCamError("invalid_response", "file upload info missing")

        # Content-Length は httpx が設定するため除外
        headers = {k: str(v) for k, v in (upload.get("headers") or {}).items() if k.lower() != "content-length"}
        put = await client.request(upload.get("method", "PUT"), upload["url"], headers=headers, content=jpeg)
        if put.status_code >= 400:
            raise YouCamError("upload_failed", f"HTTP {put.status_code}")

        self._file_ids[key] = (file_id, time.time())
        return file_id

    async def _run_task(self, client: httpx.AsyncClient, feature: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        res = await client.post(f"{self.base_url}/s2s/v2.0/task/{feature}", headers=self._auth(), json=payload)
        body = self._json_or_raise(res)
        task_id = (body.get("data") or {}).get("task_id")
        if not task_id:
            raise YouCamError("invalid_response", "task_id missing")

        deadline = time.monotonic() + self.poll_timeout
        while True:
            res = await client.get(f"{self.base_url}/s2s/v2.0/task/{feature}/{task_id}", headers=self._auth())
            data = self._json_or_raise(res).get("data") or {}
            status = data.get("task_status")
            if status == "success":
                return data.get("results") or {}
            if status == "error":
                raise YouCamError(data.get("error") or "task_error", data.get("error_message") or "")
            if time.monotonic() >= deadline:
                raise YouCamError("poll_timeout", f"{feature} task {task_id} still {status}")
            await asyncio.sleep(self.poll_interval)

    @staticmethod
    def _json_or_raise(res: httpx.Response) -> Dict[str, Any]:
        try:
            body = res.json()
        except ValueError:
            body = {}
        if res.status_code >= 400:
            code = body.get("error_code") or body.get("error") or f"http_{res.status_code}"
            raise YouCamError(str(code), body.get("error_message") or body.get("message") or "")
        return body
