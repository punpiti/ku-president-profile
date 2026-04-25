from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "articles_data" / "articles.json"

REQUIRED_FIELDS = {
    "slug": str,
    "page_title": str,
    "rewrite_title": str,
    "meta_description": str,
    "hero_kicker": str,
    "hero_subtitle": str,
    "category": str,
    "date": str,
    "source_label": str,
    "source_url": str,
    "image": str,
    "image_index": str,
    "image_alt": str,
    "summary": str,
    "title_max": str,
    "subtitle_max": str,
    "tags": list,
    "intro_paragraphs": list,
    "sections": list,
    "original_text": str,
}

OPTIONAL_FIELDS = {
    "read_more": dict,
}

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_articles() -> list[dict]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(message)


def validate_iso_date(value: str, slug: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        fail(f"{slug}: invalid date '{value}' ({exc})")


def validate_image(path_value: str, slug: str) -> None:
    normalized = path_value[3:] if path_value.startswith("../") else path_value
    candidate = ROOT / "docs" / normalized
    if not candidate.exists():
        fail(f"{slug}: image file not found at '{path_value}'")


def image_asset_path(path_value: str) -> str:
    return path_value[3:] if path_value.startswith("../") else path_value


def validate_image_naming(article: dict, image_usage_counts: Counter[str]) -> None:
    slug = article["slug"]
    image_path = article["image"]
    image_index_path = article["image_index"]
    normalized_image = image_asset_path(image_path)
    normalized_index = image_asset_path(image_index_path)

    if normalized_image != normalized_index:
        fail(
            f"{slug}: image and image_index must point to the same asset "
            f"('{image_path}' vs '{image_index_path}')"
        )

    if image_usage_counts[normalized_index] > 1:
        return

    expected = f"assets/{slug}{Path(normalized_index).suffix}"
    if normalized_index != expected:
        fail(
            f"{slug}: non-shared article image must be named after slug "
            f"(expected '{expected}', got '{normalized_index}')"
        )


def validate_article(article: dict, seen_slugs: set[str]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in article]
    if missing:
        fail(f"missing fields in article: {', '.join(missing)}")

    slug = article["slug"]
    if not isinstance(slug, str) or not SLUG_PATTERN.match(slug):
        fail(f"{slug!r}: slug must be lowercase kebab-case")
    if slug in seen_slugs:
        fail(f"{slug}: duplicate slug")
    seen_slugs.add(slug)

    for field, expected_type in REQUIRED_FIELDS.items():
      if not isinstance(article[field], expected_type):
          fail(f"{slug}: field '{field}' must be {expected_type.__name__}")
      if expected_type is str and not article[field].strip():
          fail(f"{slug}: field '{field}' must not be empty")

    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in article and not isinstance(article[field], expected_type):
            fail(f"{slug}: optional field '{field}' must be {expected_type.__name__}")

    validate_iso_date(article["date"], slug)

    if not article["source_url"].startswith(("http://", "https://")):
        fail(f"{slug}: source_url must start with http:// or https://")

    validate_image(article["image"], slug)
    validate_image(article["image_index"], slug)

    if not article["tags"]:
        fail(f"{slug}: tags must not be empty")
    if any(not isinstance(tag, str) or not tag.strip() for tag in article["tags"]):
        fail(f"{slug}: every tag must be a non-empty string")

    if not article["intro_paragraphs"]:
        fail(f"{slug}: intro_paragraphs must not be empty")
    if any(not isinstance(p, str) or not p.strip() for p in article["intro_paragraphs"]):
        fail(f"{slug}: every intro_paragraph must be a non-empty string")

    if not article["sections"]:
        fail(f"{slug}: sections must not be empty")
    for index, section in enumerate(article["sections"], start=1):
        if not isinstance(section, dict):
            fail(f"{slug}: section #{index} must be an object")
        if "title" not in section or "paragraphs" not in section:
            fail(f"{slug}: section #{index} must contain 'title' and 'paragraphs'")
        if section["title"] is not None and not isinstance(section["title"], str):
            fail(f"{slug}: section #{index} title must be string or null")
        if not isinstance(section["paragraphs"], list) or not section["paragraphs"]:
            fail(f"{slug}: section #{index} paragraphs must be a non-empty list")
        if any(not isinstance(p, str) or not p.strip() for p in section["paragraphs"]):
            fail(f"{slug}: section #{index} paragraphs must contain non-empty strings")

    if "read_more" in article:
        validate_read_more(article["read_more"], slug)


def validate_read_more(read_more: dict, slug: str) -> None:
    required = {
        "title": str,
        "kicker": str,
        "headline": str,
        "description": str,
        "button_label": str,
        "url": str,
    }
    missing = [field for field in required if field not in read_more]
    if missing:
        fail(f"{slug}: read_more missing fields: {', '.join(missing)}")
    for field, expected_type in required.items():
        if not isinstance(read_more[field], expected_type):
            fail(f"{slug}: read_more field '{field}' must be {expected_type.__name__}")
        if not read_more[field].strip():
            fail(f"{slug}: read_more field '{field}' must not be empty")
    if not read_more["url"].startswith(("http://", "https://")):
        fail(f"{slug}: read_more url must start with http:// or https://")


def validate_articles(articles: list[dict]) -> None:
    if not isinstance(articles, list) or not articles:
        fail("articles.json must contain a non-empty list")

    image_usage_counts: Counter[str] = Counter()
    for article in articles:
        if not isinstance(article, dict):
            fail("every article entry must be an object")
        image_usage_counts[image_asset_path(article.get("image_index", ""))] += 1

    seen_slugs: set[str] = set()
    for article in articles:
        validate_article(article, seen_slugs)
        validate_image_naming(article, image_usage_counts)


def main() -> int:
    try:
        articles = load_articles()
        validate_articles(articles)
    except Exception as exc:  # noqa: BLE001
        print(f"Article validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Article validation passed: {len(articles)} article(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
