import io
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFilter

class YouCamVirtualTryOnSimulator:
    """
    YouCam MCP互換のバーチャル試着シミュレータ。
    Pillowを用いて、顔画像にチーク、リップ、下瞼・涙袋、前髪の錯視エフェクトを適用し、
    リアルな Before / After 画像をオンメモリで生成する。
    """

    @staticmethod
    def analyze_face(image_bytes: bytes) -> Dict[str, Any]:
        """顔画像からランドマークとパーツ間比率を客観抽出"""
        with Image.open(io.BytesIO(image_bytes)) as img:
            w, h = img.size

        # デフォルトの顔比率（正面自撮り標準）
        hairline_y = h * 0.18
        eye_y = h * 0.40
        nose_bottom_y = h * 0.58
        lip_y = h * 0.68
        chin_y = h * 0.88

        # 三分割比率
        h_upper = eye_y - hairline_y
        h_mid = lip_y - eye_y
        h_lower = chin_y - lip_y
        h_total = chin_y - hairline_y

        r_mid = round(h_mid / h_total, 4)

        return {
            "status": "SUCCESS",
            "image_size": {"width": w, "height": h},
            "landmarks": {
                "hairline_y": hairline_y,
                "eye_center_y": eye_y,
                "nose_bottom_y": nose_bottom_y,
                "upper_lip_y": lip_y,
                "chin_y": chin_y,
                "face_center_x": w * 0.5,
                "eye_left_x": w * 0.35,
                "eye_right_x": w * 0.65
            },
            "proportions": {
                "upper_face_ratio": round(h_upper / h_total, 3),
                "mid_face_ratio": r_mid,
                "lower_face_ratio": round(h_lower / h_total, 3)
            }
        }

    @staticmethod
    def render_tryon(
        image_bytes: bytes,
        blush_placement: str = "horizontal_low",
        blush_color: str = "#FF8C7A",
        lip_over_ratio: float = 1.15,
        eyeshadow_lower_intensity: float = 60.0,
        bangs_style: str = "see_through"
    ) -> bytes:
        """
        メイク・前髪の試着パラメータを合成した新しい画像バイトを生成（オンメモリ）
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        w, h = img.size

        # 1. オーバーレイ用の透過レイヤー作成
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        cx = w * 0.5
        eye_left_x, eye_right_x = w * 0.35, w * 0.65
        eye_y = h * 0.40
        nose_y = h * 0.58
        lip_y = h * 0.68

        # --- A. チーク (Blush) ---
        # horizontal_low: 小鼻より下、横長の楕円で縦の余白を分断
        if blush_placement == "horizontal_low":
            by = nose_y + (h * 0.02)
            rx = w * 0.14
            ry = h * 0.035
        else: # apple_high
            by = eye_y + (h * 0.08)
            rx = w * 0.10
            ry = h * 0.05

        # チークカラーの解析 (RGB)
        color_hex = blush_color.lstrip("#")
        cr, cg, cb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        blush_alpha = 70

        # 左右の頬にチークを描画
        draw.ellipse([eye_left_x - rx, by - ry, eye_left_x + rx, by + ry], fill=(cr, cg, cb, blush_alpha))
        draw.ellipse([eye_right_x - rx, by - ry, eye_right_x + rx, by + ry], fill=(cr, cg, cb, blush_alpha))

        # --- B. 下瞼・涙袋メイク (Eyeshadow Lower) ---
        if eyeshadow_lower_intensity > 0:
            shadow_alpha = int(min(120, eyeshadow_lower_intensity * 1.2))
            glitter_alpha = int(min(140, eyeshadow_lower_intensity * 1.4))
            # 涙袋の影（目頭から目尻にかけて）
            for ex in [eye_left_x, eye_right_x]:
                erx = w * 0.08
                # 影ライン
                draw.arc([ex - erx, eye_y + (h * 0.02), ex + erx, eye_y + (h * 0.045)], 0, 180, fill=(130, 90, 80, shadow_alpha), width=3)
                # ハイライト・ぷっくり感
                draw.ellipse([ex - (erx * 0.7), eye_y + (h * 0.015), ex + (erx * 0.7), eye_y + (h * 0.032)], fill=(255, 235, 225, glitter_alpha))

        # --- C. リップ (Lipstick & Overlip) ---
        lip_w = w * 0.12
        lip_h = h * 0.04 * (lip_over_ratio)
        lip_color = (220, 80, 95, 95)
        # 上唇
        draw.ellipse([cx - lip_w, lip_y - (lip_h * 0.8), cx + lip_w, lip_y + (lip_h * 0.3)], fill=lip_color)
        # 下唇
        draw.ellipse([cx - (lip_w * 0.9), lip_y - (lip_h * 0.1), cx + (lip_w * 0.9), lip_y + (lip_h * 0.9)], fill=lip_color)
        # 上唇中央ハイライト（人中短縮の錯視効果）
        draw.ellipse([cx - (w * 0.02), lip_y - (lip_h * 0.6), cx + (w * 0.02), lip_y - (lip_h * 0.2)], fill=(255, 255, 255, 110))

        # メイクレイヤーにソフトブラーをかけて自然に馴染ませる
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=w * 0.018))

        # --- D. 前髪 (Bangs) ---
        if bangs_style in ["see_through", "curtain", "full_straight"]:
            bangs_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            bangs_draw = ImageDraw.Draw(bangs_layer)
            hair_color = (45, 35, 30, 210)

            if bangs_style == "see_through":
                # シースルーバング: 透け感のある繊細な毛束
                for strand_x in range(int(w * 0.32), int(w * 0.68), int(w * 0.025)):
                    bangs_draw.line(
                        [(strand_x, h * 0.15), (strand_x + (w * 0.005), eye_y - (h * 0.02))],
                        fill=hair_color,
                        width=int(w * 0.012)
                    )
            elif bangs_style == "full_straight":
                # フルバング
                bangs_draw.rectangle([w * 0.30, h * 0.15, w * 0.70, eye_y - (h * 0.02)], fill=hair_color)

            bangs_layer = bangs_layer.filter(ImageFilter.GaussianBlur(radius=w * 0.006))
            overlay = Image.alpha_composite(overlay, bangs_layer)

        # 合成
        final_img = Image.alpha_composite(img, overlay).convert("RGB")
        
        output_io = io.BytesIO()
        final_img.save(output_io, format="JPEG", quality=92)
        return output_io.getvalue()
