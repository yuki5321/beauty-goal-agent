from typing import Dict, Any, Tuple

class ProportionAnalyzer:
    """
    顔パーツ比率の幾何学的・客観的測定とゴールスコア算出
    """

    @staticmethod
    def calculate_midface_ratio(landmarks: Dict[str, Any]) -> float:
        """
        中顔面比率 R_mid = H_mid / H_total を算出
        landmarks:
          - eye_center_y: 目の中心Y座標
          - upper_lip_y: 上唇中央Y座標
          - hairline_y: 額生え際Y座標
          - chin_y: 顎先Y座標
        """
        eye_y = landmarks.get("eye_center_y", 200.0)
        lip_y = landmarks.get("upper_lip_y", 350.0)
        hairline_y = landmarks.get("hairline_y", 100.0)
        chin_y = landmarks.get("chin_y", 500.0)

        h_mid = max(1.0, lip_y - eye_y)
        h_total = max(1.0, chin_y - hairline_y)

        r_mid = h_mid / h_total
        return round(r_mid, 4)

    @staticmethod
    def ideal_ratio(goal: str) -> float:
        """Goalごとの目標とする見かけの中顔面比率"""
        if goal == "midface_shortening" or "中顔面" in goal:
            return 0.31
        if goal == "small_face" or "小顔" in goal:
            return 0.32
        return 0.315

    @staticmethod
    def calculate_goal_score(goal: str, perceived_ratio: float, alpha: float = 8.0) -> int:
        """
        第2部 3.1 式:
        Goal Score = max(0, min(100, round(100 - alpha * |R_perceived - R_ideal| * k)))
        """
        diff = abs(perceived_ratio - ProportionAnalyzer.ideal_ratio(goal))
        # 小顔目標は比率差への感度をやや緩める
        k = 90.0 if (goal == "small_face" or "小顔" in goal) else 100.0
        score = 100.0 - (alpha * diff * k)
        return max(0, min(100, int(round(score))))

    @staticmethod
    def simulate_perceived_ratio_shift(
        current_ratio: float,
        blush_placement: str,
        lip_over_ratio: float,
        eyeshadow_lower_intensity: float,
        bangs_style: str,
        blush_intensity: float = 45.0
    ) -> float:
        """
        メイク・ヘアの錯視パラメータによる見かけの中顔面比率のシフト量を計算
        - blush_placement == 'horizontal_low': チークが顔の縦余白を横に分断 (-0.015)
        - lip_over_ratio: 上唇オーバーリップで人中短縮 (1.0 -> 0, 1.2 -> -0.012)
        - eyeshadow_lower_intensity: 涙袋・下瞼強調で目の重心が下がる (-0.010)
        - bangs_style == 'see_through': 前髪で上顔面境界を押し下げ (-0.008)
        """
        shift = 0.0

        # チークの濃さで分断効果を増減（濃さ45で係数1.0）
        blush_factor = 0.5 + max(0.0, blush_intensity) / 90.0
        if blush_placement == "horizontal_low":
            shift -= 0.018 * blush_factor
        elif blush_placement == "apple_high":
            shift -= 0.005 * blush_factor

        if lip_over_ratio > 1.0:
            shift -= (lip_over_ratio - 1.0) * 0.08  # 例: 1.15なら約 -0.012

        if eyeshadow_lower_intensity > 0:
            shift -= (eyeshadow_lower_intensity / 100.0) * 0.012

        if bangs_style == "see_through":
            shift -= 0.010
        elif bangs_style == "full_straight":
            shift -= 0.006

        perceived = max(0.25, current_ratio + shift)
        return round(perceived, 4)
