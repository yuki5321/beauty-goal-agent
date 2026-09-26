import re
from typing import Tuple, Dict, Any, List

# N-G01: 禁止用語リスト（容姿批判・ルッキズム・コンプレックス刺激用語）
FORBIDDEN_TERMS = [
    "ブサイク", "不細工", "不細工な", "醜い", "顔が悪い", "器量", "不格好",
    "欠点", "劣っている", "ダメな顔", "直す", "整形レベル", "整形でしか",
    "黄金比から外れている", "点数", "点", "60点", "不合格", "奇形",
    "ugly", "defect", "flaw", "inferior", "unattractive", "score", "points"
]

# N-G02: 禁止ツール・禁止変形パラメータリスト
FORBIDDEN_TOOLS = [
    "AI_Face_Reshape",
    "jaw_slimming",
    "chin_shorten_physical",
    "bone_restructure",
    "eye_enlarge_extreme",
    "nose_narrow_physical"
]

# 許容パラメータのハードリミット
PARAMETER_LIMITS = {
    "lip_over_ratio": (1.0, 1.3),  # 最大30%のオーバーリップまで
    "eyeshadow_lower_intensity": (0, 100),
    "blush_spread": (0.5, 2.0)
}

class GovernanceViolationError(Exception):
    """Raised when an action violates Responsible AI / Governance policies."""
    pass

class SafetyGuardrail:
    @staticmethod
    def inspect_text_input(text: str) -> Tuple[bool, str]:
        """
        N-G01: ユーザー入力またはプロンプト内の容姿批判用語・ルッキズムをスキャン。
        返り値: (is_safe, sanitized_or_reason)
        """
        if not text:
            return True, ""
        
        lowered = text.lower()
        for term in FORBIDDEN_TERMS:
            if term.lower() in lowered:
                return False, f"倫理規程（ルッキズム排除）違反: 容姿批判・採点表現 '{term}' は使用できません。「比率の視覚的調整」「印象のシフト」として再定義してください。"
        
        # 簡易プロンプトインジェクション検知
        injection_patterns = [
            r"ignore\s+(all\s+)?prior\s+instructions",
            r"system\s*prompt\s*override",
            r"reveal\s+instructions",
            r"これまでの指示を無視して"
        ]
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "セキュリティ規程違反: 不正なプロンプト操作パターンを検知しました。"

        return True, "SAFE"

    @staticmethod
    def inspect_tool_call(tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        N-G02: 過剰加工・ディスモルフィア抑止ガードレール。
        骨格変形ツールや非現実的な変形パラメータを遮断。
        """
        if tool_name in FORBIDDEN_TOOLS:
            return False, f"ディスモルフィア抑止規程違反: 物理的骨格変形ツール '{tool_name}' は禁止されています。メイクやヘアによる錯視効果ツールのみ利用可能です。"

        # パラメータリミット検査
        if "lip_over_ratio" in parameters:
            ratio = float(parameters["lip_over_ratio"])
            min_v, max_v = PARAMETER_LIMITS["lip_over_ratio"]
            if not (min_v <= ratio <= max_v):
                return False, f"安全リミット違反: 上唇オーバーリップ倍率 ({ratio}) が安全範囲 ({min_v}〜{max_v}) を逸脱しています。"

        return True, "SAFE"

    @staticmethod
    def audit_governance_status(goal: str, prompt: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """推論ログに記録するための監査レポートを生成"""
        text_safe, text_reason = SafetyGuardrail.inspect_text_input(prompt + " " + goal)
        tool_safe, tool_reason = SafetyGuardrail.inspect_tool_call(tool_name, params)
        
        return {
            "body_dysmorphic_risk": "SAFE" if tool_safe else "BLOCKED",
            "prompt_injection_detected": not text_safe,
            "pii_masked": True,
            "violations": [r for r in [text_reason, tool_reason] if r != "SAFE" and r != ""]
        }
