"""
YouCam API の疎通確認スクリプト（Cloud Shell などキーを持つ環境で実行）。

使い方（backend ディレクトリで）:
  PYTHONPATH=. python scripts/youcam_smoke.py --catalog            # パターン一覧の表示のみ（ユニット消費なし）
  PYTHONPATH=. python scripts/youcam_smoke.py path/to/selfie.jpg   # 顔分析 + メイク試着1回（約11ユニット消費）

環境変数 YOUCAM_API_KEY（必須）、YOUCAM_BASE_URL（任意）を使用します。
"""
import argparse
import asyncio
import os
import sys
import httpx

CATALOG_BASE = "https://plugins-media.makeupar.com/wcm-saas"
CATALOGS = {
    "blush": f"{CATALOG_BASE}/patterns/blush.json",
    "lipliner": f"{CATALOG_BASE}/patterns/lipliner.json",
    "highlighter": f"{CATALOG_BASE}/patterns/highlighter.json",
    "eyeshadow": f"{CATALOG_BASE}/patterns/eyeshadow.json",
    "lipshape": f"{CATALOG_BASE}/shapes/lipshape.json",
}


def _labels(node):
    """カタログJSONから label を再帰的に集める（構造に依存しない）"""
    if isinstance(node, dict):
        if "label" in node:
            yield node["label"]
        for value in node.values():
            yield from _labels(value)
    elif isinstance(node, list):
        for value in node:
            yield from _labels(value)


async def show_catalogs() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        for name, url in CATALOGS.items():
            try:
                res = await client.get(url)
                res.raise_for_status()
                labels = list(dict.fromkeys(_labels(res.json())))
                print(f"[{name}] {len(labels)} patterns: {', '.join(map(str, labels[:60]))}")
            except Exception as e:
                print(f"[{name}] failed to load {url}: {e}")


async def run_smoke(image_path: str) -> None:
    from app.config import settings
    from app.mcp.youcam_api import YouCamAPI
    from app.mcp.youcam_mapping import plan_to_effects

    if not settings.YOUCAM_API_KEY:
        sys.exit("YOUCAM_API_KEY が設定されていません。")
    with open(image_path, "rb") as f:
        image = f.read()

    plan = {
        "blush_placement": "horizontal_low",
        "blush_color": "#FF8C7A",
        "lip_over_ratio": 1.15,
        "eyeshadow_lower_intensity": 70.0,
        "bangs_style": "none",
    }
    print(f"Base URL: {settings.YOUCAM_BASE_URL}")
    print("この確認で約11ユニット（顔分析10 + メイク試着1）を消費します。")
    if input("続行しますか？ [y/N]: ").strip().lower() != "y":
        return

    api = YouCamAPI(settings.YOUCAM_BASE_URL, settings.YOUCAM_API_KEY, poll_timeout=settings.YOUCAM_POLL_TIMEOUT)
    analysis = await api.analyze_face(image)
    print(f"顔分析 horizontal_third: {analysis['horizontal_third']} → 中顔面比率 {analysis['proportions']['mid_face_ratio']}")

    print("送信する effects:", plan_to_effects(plan))
    result = await api.apply_makeup(image, plan)
    out = os.path.abspath("youcam_result.jpg")
    with open(out, "wb") as f:
        f.write(result)
    print(f"試着結果を保存しました: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", nargs="?", help="顔写真（正面・顔全体が写ったJPEG/PNG）")
    parser.add_argument("--catalog", action="store_true", help="パターンカタログのラベル一覧を表示")
    args = parser.parse_args()

    if args.catalog:
        asyncio.run(show_catalogs())
    if args.image:
        asyncio.run(run_smoke(args.image))
    if not args.catalog and not args.image:
        parser.print_help()


if __name__ == "__main__":
    main()
