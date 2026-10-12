import io
import json
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
from app.config import settings
from app.agent import gemini
from app.agent.prompts import CRITIC_SYSTEM_INSTRUCTION
from app.agent.proportion import ProportionAnalyzer
from app.governance.guardrail import SafetyGuardrail
from app.observability.logger import agent_logger

# 1回のReplanで動かす各レバーの調整幅
EYESHADOW_STEP = 25.0
LIP_OVER_STEP = 0.05
LIP_OVER_SOFT_MAX = 1.25  # ガードレール上限(1.3)より手前で止める
# 目標比率からこの範囲内なら調整不要とみなす
RATIO_TOLERANCE = 0.005

# Critic の要素別スコアから総合点を出す重み（前髪が評価対象外なら残りで正規化）
ELEMENT_WEIGHTS = {"blush": 0.3, "lip": 0.25, "under_eye": 0.25, "bangs": 0.2}
ELEMENT_LABELS = {"blush": "チーク", "lip": "リップ", "under_eye": "涙袋", "bangs": "前髪"}


def _score_value(value: Any) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return max(0, min(100, int(round(value))))


def combine_element_scores(element_scores: Dict[str, Any], include_bangs: bool) -> Tuple[Optional[int], Dict[str, int]]:
    """要素別スコアの重み付き平均。戻り値: (総合点, 採用した要素別スコア)"""
    used: Dict[str, int] = {}
    for key in ELEMENT_WEIGHTS:
        if key == "bangs" and not include_bangs:
            continue
        value = _score_value(element_scores.get(key))
        if value is not None:
            used[key] = value
    total_weight = sum(ELEMENT_WEIGHTS[k] for k in used)
    if total_weight <= 0:
        return None, {}
    score = sum(ELEMENT_WEIGHTS[k] * v for k, v in used.items()) / total_weight
    return int(round(score)), used


def _detect_mime(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            return Image.MIME.get(img.format, "image/jpeg")
    except Exception:
        return "image/jpeg"


class VisualCriticAgent:
    """
    Geminiマルチモーダル機能を用いた自己評価（Critic）エージェント。
    画像上の錯視効果によるGoal達成率（0〜100%）を客観評価し、
    反省（Reflection）と再調整パラメータを生成する。
    """

    async def evaluate_tryon(
        self,
        original_image_bytes: bytes,
        simulated_image_bytes: bytes,
        goal: str,
        current_parameters: Dict[str, Any],
        iteration: int,
        base_ratio: float,
        bangs_rendered: bool = True
    ) -> Dict[str, Any]:
        """マルチモーダル評価を実行"""
        # Gemini API キーがある場合は Gemini によるマルチモーダル推論を試行
        if gemini.is_available():
            parsed = await gemini.generate_json(
                CRITIC_SYSTEM_INSTRUCTION,
                self._gemini_contents(original_image_bytes, simulated_image_bytes, goal, current_parameters, iteration, bangs_rendered),
                temperature=0.2
            )
            include_bangs = bangs_rendered and current_parameters.get("bangs_style", "none") != "none"
            normalized = self._normalize_gemini_result(parsed, current_parameters, include_bangs)
            if normalized:
                return normalized
            agent_logger.info("Gemini critic returned no usable result, using rule-based critic.")

        # フォールバック: 幾何学的比率計算による客観評価
        return self._rule_based_critic(goal, current_parameters, base_ratio)

    @staticmethod
    def _gemini_contents(
        original_image_bytes: bytes,
        simulated_image_bytes: bytes,
        goal: str,
        current_parameters: Dict[str, Any],
        iteration: int,
        bangs_rendered: bool = True
    ) -> List[Any]:
        from google.genai import types

        prompt = f"""
Goal: {goal}
試行反復回数: {iteration} 回目
現在の適用パラメータ: {json.dumps(current_parameters, ensure_ascii=False)}

1枚目の元画像と2枚目のメイク・前髪試着後画像を比較し、
指定されたGoalに対する達成度を評価して指定JSONスキーマのみで回答してください。
"""
        if not bangs_rendered:
            prompt += "\n※前髪（bangs_style）は試着画像に反映されていないため、前髪の効果は評価対象外とし、チーク・リップ・涙袋のみで評価してください。\n"
        return [
            types.Part.from_bytes(data=original_image_bytes, mime_type=_detect_mime(original_image_bytes)),
            types.Part.from_bytes(data=simulated_image_bytes, mime_type=_detect_mime(simulated_image_bytes)),
            prompt
        ]

    def _normalize_gemini_result(self, parsed: Any, params: Dict[str, Any], include_bangs: bool = True) -> Dict[str, Any]:
        """
        Geminiの出力を検証する。総合点は要素別スコアの重み付き平均をコードで算出し、
        要素別スコアが無い場合のみ goal_similarity_score を使う。パラメータは安全リミット内に収める。
        """
        if not isinstance(parsed, dict):
            return {}
        element_scores = parsed.get("element_scores")
        score, used = combine_element_scores(element_scores, include_bangs) if isinstance(element_scores, dict) else (None, {})
        if score is None:
            score = _score_value(parsed.get("goal_similarity_score"))
        if score is None:
            return {}

        recommended = parsed.get("recommended_adjustment")
        merged = dict(params)
        if isinstance(recommended, dict):
            merged.update({k: v for k, v in recommended.items() if k in params})

        feedback = str(parsed.get("critic_feedback", ""))
        if used:
            breakdown = " / ".join(f"{ELEMENT_LABELS[k]} {v}" for k, v in used.items())
            feedback = f"（{breakdown}）{feedback}"
        return {
            "goal_similarity_score": score,
            "is_goal_met": score >= settings.SCORE_CONVERGENCE_THRESHOLD,
            "element_scores": used,
            "critic_feedback": feedback,
            "recommended_adjustment": SafetyGuardrail.clamp_parameters(merged)
        }

    def _rule_based_critic(
        self,
        goal: str,
        params: Dict[str, Any],
        base_ratio: float
    ) -> Dict[str, Any]:
        """観測した中顔面比率と錯視シフトモデルに基づく批評生成"""
        perceived = ProportionAnalyzer.simulate_perceived_ratio_shift(
            base_ratio,
            params.get("blush_placement", "horizontal_low"),
            float(params.get("lip_over_ratio", 1.0)),
            float(params.get("eyeshadow_lower_intensity", 0.0)),
            params.get("bangs_style", "none")
        )
        score = ProportionAnalyzer.calculate_goal_score(goal, perceived)
        is_met = score >= settings.SCORE_CONVERGENCE_THRESHOLD
        ideal = ProportionAnalyzer.ideal_ratio(goal)

        adjustments, changes = self._propose_adjustment(params, perceived - ideal)

        status = f"見かけの中顔面比率 {base_ratio:.3f} → {perceived:.3f}（目標 {ideal:.3f}）。"
        if is_met:
            feedback = status + "現在のパラメータで目標バランスへの印象シフトが得られている。"
        elif changes:
            reason = "まだ縦の余白の印象が残るため、" if perceived > ideal else "錯視が効きすぎて目標比率を下回るため、"
            feedback = status + reason + "、".join(changes) + "を提案。"
        else:
            feedback = status + "メイク・前髪で安全に動かせる調整余地を使い切った。"

        return {
            "goal_similarity_score": score,
            "is_goal_met": is_met,
            "perceived_midface_ratio": perceived,
            "critic_feedback": feedback,
            "recommended_adjustment": adjustments
        }

    @staticmethod
    def _propose_adjustment(params: Dict[str, Any], gap: float) -> Tuple[Dict[str, Any], List[str]]:
        """
        目標とのギャップ方向に、安全範囲内で錯視レバーを1段階ずつ動かす。
        gap > 0: まだ縦に長く見える（シフトを強める） / gap < 0: 行き過ぎ（弱める）
        """
        adjusted = dict(params)
        changes: List[str] = []
        if abs(gap) <= RATIO_TOLERANCE:
            return adjusted, changes

        eyeshadow = float(params.get("eyeshadow_lower_intensity", 0.0))
        lip = float(params.get("lip_over_ratio", 1.0))

        if gap > 0:
            if params.get("blush_placement") != "horizontal_low":
                adjusted["blush_placement"] = "horizontal_low"
                changes.append("チークを小鼻下の横長配置へ移動")
            if eyeshadow < 100.0:
                adjusted["eyeshadow_lower_intensity"] = min(100.0, eyeshadow + EYESHADOW_STEP)
                changes.append(f"涙袋シャドウを{eyeshadow:.0f}%→{adjusted['eyeshadow_lower_intensity']:.0f}%へ強調")
            if lip < LIP_OVER_SOFT_MAX:
                adjusted["lip_over_ratio"] = round(min(LIP_OVER_SOFT_MAX, lip + LIP_OVER_STEP), 2)
                changes.append(f"オーバーリップをx{lip:.2f}→x{adjusted['lip_over_ratio']:.2f}へ拡張")
            if params.get("bangs_style") != "see_through":
                adjusted["bangs_style"] = "see_through"
                changes.append("前髪をシースルーバングへ変更")
        else:
            if eyeshadow > 0.0:
                adjusted["eyeshadow_lower_intensity"] = max(0.0, eyeshadow - EYESHADOW_STEP)
                changes.append(f"涙袋シャドウを{eyeshadow:.0f}%→{adjusted['eyeshadow_lower_intensity']:.0f}%へ控えめに")
            if lip > 1.0:
                adjusted["lip_over_ratio"] = round(max(1.0, lip - LIP_OVER_STEP), 2)
                changes.append(f"オーバーリップをx{lip:.2f}→x{adjusted['lip_over_ratio']:.2f}へ抑制")

        return SafetyGuardrail.clamp_parameters(adjusted), changes


critic_agent = VisualCriticAgent()
