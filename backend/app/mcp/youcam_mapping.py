"""
スタイリングパラメータ → YouCam makeup-vto の effects 変換。

パターン名は YouCam のパターンカタログのラベルと一致している必要がある:
  https://plugins-media.makeupar.com/wcm-saas/patterns/blush.json
  https://plugins-media.makeupar.com/wcm-saas/patterns/lipliner.json
  https://plugins-media.makeupar.com/wcm-saas/patterns/highlighter.json
  https://plugins-media.makeupar.com/wcm-saas/shapes/lipshape.json
チークはカタログの形状タグで選んでいる（backend/scripts/youcam_smoke.py --catalog でタグ付き一覧を表示できる）。
horizontal_low の 1color1 は実APIの試着結果で見た目を確認済み。
"""
import json
import os
from typing import Any, Dict, List, Optional

BLUSH_PATTERNS = {
    "horizontal_low": "1color1",   # tag: Oblong（横長）
    "apple_high": "1color6",       # tag: Circle（頬の高い位置に丸く）
    "diagonal_temple": "1color3",  # tag: Rectangle（斜め・こめかみ方向）
}
LIP_LINER_NATURAL = "Natural1"
LIP_LINER_OVER_UPPER = "LargerUpper1"
LIP_SHAPE = "original"  # 唇の形を変える plump 等や morphology は N-G02 に従い使わない
HIGHLIGHTER_PATTERN = "SquareFace3"

# 前髪スタイル → YouCam hair-bang テンプレートID（系統は利用者が画面で選択。写真から推定しない）。
# 一覧は backend/scripts/youcam_smoke.py --bang-templates で確認できる。
# 環境変数 YOUCAM_BANG_TEMPLATES（JSON）で上書き可能:
#   {"male": {"see_through": "xxx"}} → その系統のみ / {"see_through": "xxx"} → 両系統
BANG_SETS = ("female", "male")
DEFAULT_BANG_SET = "female"
BANG_TEMPLATES: Dict[str, Dict[str, str]] = {
    "female": {
        "see_through": "female_wispy_bangs",
        "curtain": "female_split_bangs",
        "full_straight": "female_blunt_bangs",
    },
    "male": {
        "see_through": "male_wispy_bangs",
        "curtain": "male_split_bangs",
        "full_straight": "male_blunt_bangs",
    },
}

LIP_COLOR = "#D9737A"
CONCEALER_COLOR = "#F2D6C4"
HIGHLIGHTER_COLOR = "#FFF4EC"


def _pct(value: float) -> int:
    return max(0, min(100, int(round(value))))


def plan_to_effects(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    placement = plan.get("blush_placement", "horizontal_low")
    lip_over = float(plan.get("lip_over_ratio", 1.0))
    under_eye = float(plan.get("eyeshadow_lower_intensity", 0.0))

    effects: List[Dict[str, Any]] = [
        {
            "category": "blush",
            "pattern": {"name": BLUSH_PATTERNS.get(placement, BLUSH_PATTERNS["horizontal_low"])},
            "palettes": [{"color": plan.get("blush_color", "#FF8C7A"), "texture": "matte", "colorIntensity": 55}],
        },
        {
            "category": "lip_liner",
            "pattern": {"name": LIP_LINER_OVER_UPPER if lip_over > 1.0 else LIP_LINER_NATURAL},
            "palettes": [{
                "color": LIP_COLOR,
                "texture": "matte",
                "colorIntensity": 60,
                "thickness": _pct(30 + (lip_over - 1.0) / 0.3 * 50),
                "smoothness": 60,
            }],
        },
        {
            "category": "lip_color",
            "shape": {"name": LIP_SHAPE},
            "style": {"type": "full"},
            "palettes": [{"color": LIP_COLOR, "texture": "sheer", "colorIntensity": 60, "transparencyIntensity": 40}],
        },
    ]

    if under_eye > 0:
        effects.append({
            "category": "concealer",
            "palettes": [{
                "color": CONCEALER_COLOR,
                "colorIntensity": _pct(under_eye * 0.3),
                "colorUnderEyeIntensity": _pct(under_eye),
                "coverageLevel": 40,
            }],
        })
        effects.append({
            "category": "highlighter",
            "pattern": {"name": HIGHLIGHTER_PATTERN},
            "palettes": [{
                "color": HIGHLIGHTER_COLOR,
                "glowIntensity": _pct(under_eye * 0.5),
                "shimmerIntensity": _pct(under_eye * 0.4),
                "shimmerDensity": 40,
                "shimmerSize": 30,
                "colorIntensity": _pct(under_eye * 0.6),
            }],
        })
    return effects


def normalize_bang_set(bang_set: Optional[str]) -> str:
    return bang_set if bang_set in BANG_SETS else DEFAULT_BANG_SET


def bang_template_for(style: str, bang_set: str = DEFAULT_BANG_SET) -> Optional[str]:
    """前髪スタイル・系統に対応するテンプレートID。none・未設定は None"""
    if not style or style == "none":
        return None
    bang_set = normalize_bang_set(bang_set)
    templates = dict(BANG_TEMPLATES[bang_set])
    override = os.getenv("YOUCAM_BANG_TEMPLATES", "")
    if override:
        try:
            parsed = json.loads(override)
            if isinstance(parsed.get(bang_set), dict):
                templates.update({k: str(v) for k, v in parsed[bang_set].items()})
            templates.update({k: str(v) for k, v in parsed.items() if not isinstance(v, dict)})
        except (ValueError, AttributeError):
            pass
    return templates.get(style) or None
