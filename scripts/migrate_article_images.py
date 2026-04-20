from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "articles_data" / "articles.json"
DOCS_ASSETS_DIR = ROOT / "docs" / "assets"


def load_articles() -> list[dict]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def normalized_asset_path(path_value: str) -> str:
    return path_value[3:] if path_value.startswith("../") else path_value


def desired_asset_path(slug: str, current_path: str) -> str:
    return f"assets/{slug}{Path(current_path).suffix}"


def build_plan(articles: list[dict]) -> tuple[list[dict], list[dict]]:
    image_usage = Counter(normalized_asset_path(article["image_index"]) for article in articles)
    migrations: list[dict] = []
    skipped: list[dict] = []

    for article in articles:
        current_asset = normalized_asset_path(article["image_index"])
        if image_usage[current_asset] > 1:
            skipped.append(
                {
                    "slug": article["slug"],
                    "reason": "shared-image",
                    "asset": current_asset,
                }
            )
            continue

        target_asset = desired_asset_path(article["slug"], current_asset)
        if current_asset == target_asset:
            continue

        migrations.append(
            {
                "slug": article["slug"],
                "source_asset": current_asset,
                "target_asset": target_asset,
                "source_image": article["image"],
                "target_image": f"../{target_asset}",
            }
        )

    return migrations, skipped


def apply_migrations(articles: list[dict], migrations: list[dict], *, copy: bool) -> None:
    plan_by_slug = {item["slug"]: item for item in migrations}

    for article in articles:
        plan = plan_by_slug.get(article["slug"])
        if not plan:
            continue
        article["image"] = plan["target_image"]
        article["image_index"] = plan["target_asset"]

    DATA_FILE.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for plan in migrations:
        src = ROOT / "docs" / plan["source_asset"]
        dst = ROOT / "docs" / plan["target_asset"]
        if not src.exists():
            raise FileNotFoundError(f"source image not found: {src}")
        if dst.exists():
            continue
        if copy:
            shutil.copy2(src, dst)
        else:
            src.rename(dst)


def print_plan(migrations: list[dict], skipped: list[dict], *, copy: bool) -> None:
    mode = "copy" if copy else "rename"
    print(f"Found {len(migrations)} non-shared article image migration(s) to {mode}.")
    for plan in migrations:
        print(f"- {plan['slug']}: {plan['source_asset']} -> {plan['target_asset']}")

    if skipped:
        print(f"Skipped {len(skipped)} article(s) because the image asset is shared:")
        for item in skipped:
            print(f"- {item['slug']}: {item['asset']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rename or copy non-shared article images so the asset filename matches the article slug, "
            "and update articles_data/articles.json to reference the new paths."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the updated JSON and move/copy image files. Without this flag, only print the plan.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy images instead of renaming them. Useful when you want to keep legacy filenames around.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    articles = load_articles()
    migrations, skipped = build_plan(articles)
    print_plan(migrations, skipped, copy=args.copy)

    if not args.apply:
        print("Dry run only. Re-run with --apply to update files.")
        return 0

    apply_migrations(articles, migrations, copy=args.copy)
    print("Migration applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
