from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.config import settings
from app.mcp.simulator import YouCamVirtualTryOnSimulator
from app.mcp.youcam_api import YouCamAPI, YouCamError
from app.observability.logger import agent_logger


@dataclass
class TryOnResult:
    image_bytes: bytes
    source: str  # "youcam" | "simulator"
    fallback_reason: Optional[str] = None
    bangs_rendered: bool = True


class YouCamMCPClient:
    """
    YouCam API (Perfect Corp) クライアントの呼び出し口。
    APIキー設定時は実APIで顔分析・メイク試着を行い、
    未設定時・失敗時はシミュレータへフォールバックする（理由は戻り値に残す）。
    前髪の実API試着は第2段階のため、実API使用時は前髪を画像に描画しない。
    """

    def __init__(self, api: Optional[YouCamAPI] = None):
        self.use_mock = settings.USE_MOCK_YOUCAM or not bool(settings.YOUCAM_API_KEY)
        self.api = api or YouCamAPI(
            settings.YOUCAM_BASE_URL,
            settings.YOUCAM_API_KEY,
            poll_timeout=settings.YOUCAM_POLL_TIMEOUT,
        )

    @property
    def external_processor(self) -> Optional[str]:
        return None if self.use_mock else "YouCam API (Perfect Corp)"

    async def analyze_face(self, image_bytes: bytes) -> Dict[str, Any]:
        """顔パーツ比率（三分割）の抽出"""
        if not self.use_mock:
            try:
                return await self.api.analyze_face(image_bytes)
            except Exception as e:
                reason = self._reason(e)
                agent_logger.info(f"YouCam face analysis failed, falling back to simulator: {reason}")
                result = YouCamVirtualTryOnSimulator.analyze_face(image_bytes)
                result["fallback_reason"] = reason
                return result
        return YouCamVirtualTryOnSimulator.analyze_face(image_bytes)

    async def simulate_makeup_and_hair(self, image_bytes: bytes, plan: Dict[str, Any]) -> TryOnResult:
        """チーク・リップ・涙袋（＋シミュレータでは前髪）の試着画像を生成"""
        fallback_reason = None
        if not self.use_mock:
            try:
                image = await self.api.apply_makeup(image_bytes, plan)
                return TryOnResult(image, "youcam", bangs_rendered=False)
            except Exception as e:
                fallback_reason = self._reason(e)
                agent_logger.info(f"YouCam makeup try-on failed, falling back to simulator: {fallback_reason}")

        image = YouCamVirtualTryOnSimulator.render_tryon(
            image_bytes=image_bytes,
            blush_placement=plan.get("blush_placement", "horizontal_low"),
            blush_color=plan.get("blush_color", "#FF8C7A"),
            lip_over_ratio=float(plan.get("lip_over_ratio", 1.0)),
            eyeshadow_lower_intensity=float(plan.get("eyeshadow_lower_intensity", 0.0)),
            bangs_style=plan.get("bangs_style", "none")
        )
        return TryOnResult(image, "simulator", fallback_reason=fallback_reason)

    def forget(self, image_bytes: bytes) -> None:
        self.api.forget(image_bytes)

    @staticmethod
    def _reason(e: Exception) -> str:
        return e.code if isinstance(e, YouCamError) else type(e).__name__


youcam_client = YouCamMCPClient()
