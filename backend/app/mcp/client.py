import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.mcp.simulator import YouCamVirtualTryOnSimulator

class YouCamMCPClient:
    """
    YouCam (@perfectcorp/youcam-mcp) または Perfect Corp. REST API クライアント。
    APIキー設定時は本番API/MCP経由で実行し、
    未設定時またはオフラインモード時は高品位シミュレータに透過的にフォールバック。
    """

    def __init__(self):
        self.api_key = settings.YOUCAM_API_KEY
        self.base_url = settings.YOUCAM_BASE_URL
        self.use_mock = settings.USE_MOCK_YOUCAM or not bool(self.api_key)

    async def analyze_face(self, image_bytes: bytes) -> Dict[str, Any]:
        """顔パーツ比率とランドマークの抽出"""
        if self.use_mock:
            return YouCamVirtualTryOnSimulator.analyze_face(image_bytes)

        # 本番 YouCam API 呼び出し
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                files = {"file": ("face.jpg", image_bytes, "image/jpeg")}
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.post(
                    f"{self.base_url}/face/landmarks",
                    files=files,
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            # 本番接続失敗時は安全にシミュレータへフォールバック
            pass

        return YouCamVirtualTryOnSimulator.analyze_face(image_bytes)

    async def simulate_makeup_and_hair(
        self,
        image_bytes: bytes,
        blush_placement: str = "horizontal_low",
        blush_color: str = "#FF8C7A",
        lip_over_ratio: float = 1.15,
        eyeshadow_lower_intensity: float = 60.0,
        bangs_style: str = "see_through"
    ) -> bytes:
        """チーク・リップ・下瞼・前髪の試着シミュレーション画像を生成"""
        if self.use_mock:
            return YouCamVirtualTryOnSimulator.render_tryon(
                image_bytes=image_bytes,
                blush_placement=blush_placement,
                blush_color=blush_color,
                lip_over_ratio=lip_over_ratio,
                eyeshadow_lower_intensity=eyeshadow_lower_intensity,
                bangs_style=bangs_style
            )

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "blush": {"placement": blush_placement, "color": blush_color},
                    "lipstick": {"over_ratio": lip_over_ratio},
                    "eyeshadow": {"lower_intensity": eyeshadow_lower_intensity},
                    "hair": {"bangs_style": bangs_style}
                }
                files = {"file": ("face.jpg", image_bytes, "image/jpeg")}
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.post(
                    f"{self.base_url}/tryon/composite",
                    files=files,
                    data=payload,
                    headers=headers
                )
                if response.status_code == 200 and response.content:
                    return response.content
        except Exception:
            pass

        return YouCamVirtualTryOnSimulator.render_tryon(
            image_bytes=image_bytes,
            blush_placement=blush_placement,
            blush_color=blush_color,
            lip_over_ratio=lip_over_ratio,
            eyeshadow_lower_intensity=eyeshadow_lower_intensity,
            bangs_style=bangs_style
        )

youcam_client = YouCamMCPClient()
