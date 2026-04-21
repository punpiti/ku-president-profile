from __future__ import annotations

import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from validate_articles import validate_articles


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "articles_data" / "articles.json"
ARCHIVE_CONFIG_FILE = ROOT / "articles_data" / "archive_config.json"
SITE_CONFIG_FILE = ROOT / "site_config.json"
DOCS_DIR = ROOT / "docs"
ARTICLES_DIR = DOCS_DIR / "articles"
ASSETS_DIR = DOCS_DIR / "assets"

# Architecture note:
# This builder intentionally does a full rebuild on every run.
# At the current scale this keeps the workflow deterministic and avoids
# cache invalidation bugs, especially because one article change can affect:
# - its own article page
# - docs/articles.html
# - docs/assets/articles-data.js
# - related article sections in other pages
#
# If the article count grows substantially, the next safe optimization is:
# 1. keep rebuilding articles.html and articles-data.js every run
# 2. add change detection for individual article pages only
# 3. rebuild related targets for articles whose tag overlap is affected


def load_articles() -> list[dict]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def load_archive_config() -> dict:
    if not ARCHIVE_CONFIG_FILE.exists():
        return {}
    return json.loads(ARCHIVE_CONFIG_FILE.read_text(encoding="utf-8"))


def load_site_config() -> dict:
    defaults = {
        "site_url": "https://punpiti.github.io/ku-president-profile",
        "site_name": "Kasetsart University President Vision Archive",
        "default_social_image": "assets/portrait.jpg",
        "ga_measurement_id": "",
    }
    if not SITE_CONFIG_FILE.exists():
        return defaults
    loaded = json.loads(SITE_CONFIG_FILE.read_text(encoding="utf-8"))
    return {**defaults, **loaded}


def format_display_date(iso_date: str) -> str:
    return date.fromisoformat(iso_date).strftime("%d %B %Y")


def render_tags(tags: list[str]) -> str:
    return "\n".join(f'            <span class="tag">{html.escape(tag)}</span>' for tag in tags)


def join_site_url(site_url: str, path: str) -> str:
    return f"{site_url.rstrip('/')}/{path.lstrip('/')}"


def render_seo_meta(
    *,
    title: str,
    description: str,
    canonical_path: str,
    site_config: dict,
    image_path: str | None = None,
    page_type: str = "website",
    published_time: str | None = None,
) -> str:
    site_url = site_config["site_url"]
    canonical_url = join_site_url(site_url, canonical_path)
    social_image = join_site_url(site_url, image_path or site_config["default_social_image"])
    parts = [
        f'  <link rel="canonical" href="{html.escape(canonical_url)}">',
        '  <meta name="robots" content="index,follow">',
        f'  <meta property="og:site_name" content="{html.escape(site_config["site_name"])}">',
        f'  <meta property="og:type" content="{html.escape(page_type)}">',
        f'  <meta property="og:title" content="{html.escape(title)}">',
        f'  <meta property="og:description" content="{html.escape(description)}">',
        f'  <meta property="og:url" content="{html.escape(canonical_url)}">',
        f'  <meta property="og:image" content="{html.escape(social_image)}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title)}">',
        f'  <meta name="twitter:description" content="{html.escape(description)}">',
        f'  <meta name="twitter:image" content="{html.escape(social_image)}">',
    ]
    if published_time:
        parts.append(f'  <meta property="article:published_time" content="{html.escape(published_time)}">')
    return "\n".join(parts)


def render_webpage_json_ld(
    *,
    title: str,
    description: str,
    canonical_path: str,
    site_config: dict,
    image_path: str | None = None,
) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": join_site_url(site_config["site_url"], canonical_path),
        "image": join_site_url(site_config["site_url"], image_path or site_config["default_social_image"]),
    }
    return "  <script type=\"application/ld+json\">" + json.dumps(payload, ensure_ascii=False) + "</script>"


def render_article_json_ld(article: dict, site_config: dict) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["page_title"],
        "description": article["meta_description"],
        "datePublished": article["date"],
        "dateModified": article["date"],
        "mainEntityOfPage": join_site_url(site_config["site_url"], f"articles/{article['slug']}.html"),
        "image": [join_site_url(site_config["site_url"], article["image_index"])],
        "author": {
            "@type": "Person",
            "name": "รองศาสตราจารย์ ดร.พันธุ์ปิติ เปี่ยมสง่า",
        },
        "publisher": {
            "@type": "Organization",
            "name": site_config["site_name"],
        },
    }
    return "  <script type=\"application/ld+json\">" + json.dumps(payload, ensure_ascii=False) + "</script>"


def build_site_analytics(site_config: dict) -> str:
    measurement_id = site_config.get("ga_measurement_id", "").strip()
    if not measurement_id:
        return "window.KU_SITE_ANALYTICS = { enabled: false, measurementId: \"\" };\n"
    escaped_id = json.dumps(measurement_id)
    return f"""window.KU_SITE_ANALYTICS = {{ enabled: true, measurementId: {escaped_id} }};
(function () {{
  var cfg = window.KU_SITE_ANALYTICS;
  if (!cfg || !cfg.enabled || !cfg.measurementId) return;
  var script = document.createElement("script");
  script.async = true;
  script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(cfg.measurementId);
  document.head.appendChild(script);
  window.dataLayer = window.dataLayer || [];
  function gtag() {{ dataLayer.push(arguments); }}
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", cfg.measurementId);
}})();
"""


def build_sitemap(articles: list[dict], site_config: dict) -> str:
    del articles, site_config
    canonical_pattern = re.compile(r'<link rel="canonical" href="([^"]+)"', re.IGNORECASE)
    noindex_pattern = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.IGNORECASE)
    priority_paths = [
        "index.html",
        "context.html",
        "roles.html",
        "goals.html",
        "four-year-plan.html",
        "qa.html",
        "about.html",
        "articles.html",
        "article-browsing.html",
    ]
    urls_by_path: dict[str, str] = {}

    for html_path in DOCS_DIR.rglob("*.html"):
        if "assets" in html_path.parts:
            continue
        relative_path = html_path.relative_to(DOCS_DIR).as_posix()
        text = html_path.read_text(encoding="utf-8")
        if noindex_pattern.search(text):
            continue
        match = canonical_pattern.search(text)
        if not match:
            continue
        urls_by_path[relative_path] = match.group(1)

    lastmod_by_path = get_git_lastmods(urls_by_path)
    ordered_paths = [path for path in priority_paths if path in urls_by_path]
    ordered_paths.extend(sorted(path for path in urls_by_path if path not in priority_paths))
    body = "\n".join(
        (
            f"  <url><loc>{html.escape(urls_by_path[path])}</loc>"
            f"{f'<lastmod>{html.escape(lastmod_by_path[path])}</lastmod>' if path in lastmod_by_path else ''}"
            f"<changefreq>{html.escape(get_sitemap_changefreq(path))}</changefreq>"
            f"<priority>{html.escape(get_sitemap_priority(path))}</priority>"
            "</url>"
        )
        for path in ordered_paths
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def get_git_lastmods(urls_by_path: dict[str, str]) -> dict[str, str]:
    tracked_html_paths = [f"docs/{path}" for path in sorted(urls_by_path)]
    if not tracked_html_paths:
        return {}
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--format=%cs", "--name-only", "--", *tracked_html_paths],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return {}

    lastmod_by_path: dict[str, str] = {}
    current_date: str | None = None
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):
            current_date = line
            continue
        if not current_date or not line.startswith("docs/") or not line.endswith(".html"):
            continue
        relative_path = line.removeprefix("docs/")
        lastmod_by_path.setdefault(relative_path, current_date)
    return lastmod_by_path


def get_sitemap_changefreq(path: str) -> str:
    if path == "index.html":
        return "daily"
    if path in {
        "context.html",
        "roles.html",
        "goals.html",
        "four-year-plan.html",
        "qa.html",
        "about.html",
        "articles.html",
        "article-browsing.html",
    }:
        return "weekly"
    if path.startswith("articles/"):
        return "monthly"
    if path.startswith("questionnaire_viz_plotly/"):
        return "monthly"
    return "monthly"


def get_sitemap_priority(path: str) -> str:
    if path == "index.html":
        return "1.0"
    if path in {
        "context.html",
        "roles.html",
        "goals.html",
        "four-year-plan.html",
        "qa.html",
        "about.html",
        "articles.html",
        "article-browsing.html",
    }:
        return "0.8"
    if path.startswith("articles/"):
        return "0.7"
    if path.startswith("questionnaire_viz_plotly/"):
        return "0.5"
    return "0.6"


def build_robots_txt(site_config: dict) -> str:
    sitemap_url = join_site_url(site_config["site_url"], "sitemap.xml")
    return f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"


def render_article_content(article: dict) -> str:
    intro = "\n".join(f"                <p>{paragraph}</p>" for paragraph in article["intro_paragraphs"])
    sections: list[str] = []
    for section in article["sections"]:
        if section["title"]:
            sections.append(f"            <h2>{section['title']}</h2>")
        sections.extend(f"            <p>{paragraph}</p>" for paragraph in section["paragraphs"])
    return "\n".join(sections), intro


def build_related_data(articles: list[dict]) -> str:
    payload = [
        {
            "slug": article["slug"],
            "path": f"./{article['slug']}.html",
            "archive_path": f"articles/{article['slug']}.html",
            "title": article["page_title"],
            "summary": article["summary"],
            "category": article["category"],
            "date": article["date"],
            "display_date": format_display_date(article["date"]),
            "image_index": article["image_index"],
            "image_alt": article["image_alt"],
            "tags": article["tags"],
        }
        for article in articles
    ]
    return "window.ARTICLES_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"


def render_article_page(article: dict, site_config: dict) -> str:
    rendered_sections, rendered_intro = render_article_content(article)
    tags_attr = ",".join(article["tags"])
    display_date = format_display_date(article["date"])
    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(article["rewrite_title"])}</title>
  <meta name="description" content="{html.escape(article["meta_description"])}">
{render_seo_meta(
    title=article["rewrite_title"],
    description=article["meta_description"],
    canonical_path=f"articles/{article['slug']}.html",
    site_config=site_config,
    image_path=article["image_index"],
    page_type="article",
    published_time=article["date"],
)}
{render_article_json_ld(article, site_config)}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/archive-article.css">
  <style>
    :root {{
      --hero-title-max: {article["title_max"]};
      --hero-subtitle-max: {article["subtitle_max"]};
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="frame">
      <div class="inner">
        <header class="topbar">
          <div class="site-label">Kasetsart University -- The Life Systems University</div>
          <nav class="nav">
            <a href="../context.html">บริบท</a>
            <a href="../roles.html">บทบาท</a>
            <a href="../goals.html">เป้าหมาย</a>
            <a href="../strategy.html">กลยุทธ์</a>
            <a href="../four-year-plan.html">แผนสี่ปี</a>
            <a href="../articles.html" aria-current="page">บทความ</a>
            <a href="../qa.html">ถาม/ตอบ</a>
            <a href="../about.html">แนะนำตัว</a>
          </nav>
        </header>

        <section class="hero">
          <div class="hero-kicker">{html.escape(article["hero_kicker"])}</div>
          <h1>{html.escape(article["page_title"])}</h1>
          <div class="hero-subtitle">
            {article["hero_subtitle"]}
          </div>
          <div class="meta-row">
            <div class="pill">หมวด: {html.escape(article["category"])}</div>
            <div class="pill">วันที่โพสต์: {display_date}</div>
            <div class="pill">ที่มา: {html.escape(article["source_label"])}</div>
          </div>
          <div class="tag-row">
{render_tags(article["tags"])}
          </div>
        </section>

        <section class="section">
          <div class="section-title">Rewritten Post</div>
          <div class="content-panel is-interactive">
            <div class="rewrite-title">{html.escape(article["rewrite_title"])}</div>
            <div class="lead-split">
              <figure class="lead-figure">
                <a class="figure-link" href="{html.escape(article["image"])}" data-lightbox-image="{html.escape(article["image"])}">
                  <img class="post-image" src="{html.escape(article["image"])}" alt="{html.escape(article["image_alt"])}">
                </a>
                <figcaption class="figure-caption">คลิกรูปเพื่อดูภาพขยายใหญ่</figcaption>
              </figure>
              <div class="intro-copy">
{rendered_intro}
              </div>
            </div>
{rendered_sections}
          </div>
        </section>

        <section class="section">
          <div class="section-title">Original</div>
          <div class="reference-panel">
            <div class="reference-list">
              <div>ลิงก์อ้างอิง:</div>
              <a class="reference-link" href="{html.escape(article["source_url"])}" target="_blank" rel="noopener noreferrer" aria-label="เปิดโพสต์บน Facebook">f</a>
            </div>
            <details class="original-toggle">
              <summary>Original Facebook Post</summary>
              <div class="original-text">{html.escape(article["original_text"])}</div>
            </details>
          </div>
        </section>

        <section class="section">
          <div class="section-title">บทความอื่นที่เกี่ยวข้อง</div>
          <div class="reference-panel">
            <div class="related-grid" data-related-articles data-current-slug="{article["slug"]}" data-current-tags="{tags_attr}"></div>
          </div>
        </section>

        <footer class="footer">
          <div>Articles Archive</div>
          <div>วิสัยทัศน์ของ รองศาสตราจารย์ ดร.พันธุ์ปิติ เปี่ยมสง่า สำหรับการสรรหาอธิการบดีมหาวิทยาลัยเกษตรศาสตร์</div>
        </footer>
      </div>
    </section>
  </main>
  <div class="lightbox" id="lightbox" aria-hidden="true">
    <div class="lightbox-dialog" role="dialog" aria-modal="true" aria-label="ภาพขยายใหญ่">
      <button class="lightbox-close" id="lightboxClose" type="button" aria-label="ปิดภาพขยาย">×</button>
      <img class="lightbox-image" id="lightboxImage" src="" alt="">
    </div>
  </div>
  <script src="../assets/release-gate.js" defer></script>
  <script src="../assets/site-analytics.js" defer></script>
  <script src="../assets/articles-data.js" defer></script>
  <script src="../assets/related-articles.js" defer></script>
  <script src="../assets/archive-lightbox.js" defer></script>
</body>
</html>
"""


def article_auto_popularity(article: dict, category_articles: list[dict]) -> tuple[int, str]:
    article_tags = set(article["tags"])
    overlap_score = sum(
        len(article_tags.intersection(other["tags"]))
        for other in category_articles
        if other["slug"] != article["slug"]
    )
    return overlap_score, article["date"]


def render_archive_card(article: dict, *, compact: bool = False) -> str:
    display_date = format_display_date(article["date"])
    card_class = "archive-card archive-card--compact" if compact else "archive-card"
    heading_tag = "h3" if compact else "h2"
    return f"""            <a class="{card_class}" href="articles/{article["slug"]}.html">
              <img class="archive-thumb" src="{html.escape(article["image_index"])}" alt="{html.escape(article["image_alt"])}">
              <div class="archive-body">
                <div class="archive-meta">{html.escape(article["category"])} • {display_date}</div>
                <{heading_tag}>{html.escape(article["page_title"])}</{heading_tag}>
                <div class="tag-row">
{render_tags(article["tags"])}
                </div>
                <p>
                  {article["summary"]}
                </p>
              </div>
            </a>"""


def render_topic_card(category: str, articles: list[dict], total_count: int) -> str:
    links = []
    preview_count = min(3, len(articles))
    for index, article in enumerate(articles):
        hidden_attr = ' data-topic-extra hidden' if index >= preview_count else ""
        links.append(
            f"""              <li{hidden_attr}>
                <a href="articles/{article["slug"]}.html">{html.escape(article["page_title"])}</a>
              </li>"""
        )
    links_html = "\n".join(links)
    button_html = (
        '              <button class="topic-toggle" type="button" data-topic-toggle>ดูทั้งหมด</button>'
        if len(articles) > preview_count
        else ""
    )
    return f"""            <section class="topic-card">
              <div class="topic-card__eyebrow">เขียนทั้งหมด {total_count} เรื่อง</div>
              <h3>{html.escape(category)}</h3>
              <ol class="topic-list">
{links_html}
              </ol>
{button_html}
            </section>"""


def render_other_topics_card(groups: list[tuple[str, int, list[dict]]]) -> str:
    preview_count = min(3, len(groups))
    items: list[str] = []
    for index, (label, count, articles) in enumerate(groups):
        hidden_attr = ' data-topic-extra hidden' if index >= preview_count else ""
        article_links = "\n".join(
            f"""                    <li><a href="articles/{article["slug"]}.html">{html.escape(article["page_title"])}</a></li>"""
            for article in articles
        )
        items.append(
            f"""              <li{hidden_attr}>
                <details class="topic-subgroup">
                  <summary>
                    <span>{html.escape(label)}</span>
                    <strong>{count} เรื่อง</strong>
                  </summary>
                  <ol class="topic-subgroup-list">
{article_links}
                  </ol>
                </details>
              </li>"""
        )
    items_html = "\n".join(items)
    button_html = (
        '              <button class="topic-toggle" type="button" data-topic-toggle data-topic-other-toggle>ดูทั้งหมด</button>'
        if len(groups) > preview_count
        else ""
    )
    return f"""            <section class="topic-card topic-card--other">
              <div class="topic-card__eyebrow">หมวดที่เขียนน้อยกว่า</div>
              <h3>หัวข้ออื่นๆ</h3>
              <ul class="topic-summary-list">
{items_html}
              </ul>
{button_html}
            </section>"""


def render_interest_card(title: str, subtitle: str, items_html: str) -> str:
    return f"""          <section class="content-section">
            <div class="section-heading">
              <div class="section-kicker">Topics</div>
              <h2>{html.escape(title)}</h2>
              <p>{html.escape(subtitle)}</p>
            </div>
            <div class="topics-grid">
{items_html}
            </div>
          </section>"""


def render_latest_card(article: dict, *, hidden: bool = False) -> str:
    hidden_attr = ' data-latest-extra hidden' if hidden else ""
    return f"""            <div class="latest-item"{hidden_attr}>
{render_archive_card(article, compact=True)}
            </div>"""


def render_browsing_tile(article: dict) -> str:
    display_date = format_display_date(article["date"])
    return f"""      <a class="browse-tile" href="articles/{article["slug"]}.html" aria-label="{html.escape(article["page_title"])}">
        <img class="browse-tile__image" src="{html.escape(article["image_index"])}" alt="{html.escape(article["image_alt"])}" loading="lazy">
        <div class="browse-tile__overlay">
          <div class="browse-tile__meta">{html.escape(article["category"])} • {display_date}</div>
          <h2>{html.escape(article["page_title"])}</h2>
        </div>
      </a>"""


def render_articles_index(articles: list[dict], archive_config: dict, site_config: dict) -> str:
    ordered = sorted(articles, key=lambda article: article["date"], reverse=True)
    slug_lookup = {article["slug"]: article for article in ordered}

    featured_slug = archive_config.get("featured_slug")
    featured_article = slug_lookup.get(featured_slug, ordered[0])

    latest_articles = [article for article in ordered if article["slug"] != featured_article["slug"]]
    latest_primary = latest_articles[:3]
    latest_extra = latest_articles[3:]
    latest_html = "\n".join(render_latest_card(article) for article in latest_primary)
    latest_extra_html = "\n".join(render_latest_card(article, hidden=True) for article in latest_extra)

    category_counts = sorted(
        (
            (
                category,
                sum(1 for article in ordered if article["category"] == category),
            )
            for category in {article["category"] for article in ordered}
        ),
        key=lambda item: (-item[1], item[0]),
    )

    manual_popular = archive_config.get("popular_by_category", {})
    topic_cards: list[str] = []
    primary_categories = category_counts[:5]
    secondary_categories = category_counts[5:]

    for category, total_count in primary_categories:
        category_articles = [article for article in ordered if article["category"] == category]
        preferred = []
        for slug in manual_popular.get(category, []):
            article = slug_lookup.get(slug)
            if article and article["category"] == category and article["slug"] not in {item["slug"] for item in preferred}:
                preferred.append(article)

        remaining = [
            article
            for article in sorted(
                category_articles,
                key=lambda item: article_auto_popularity(item, category_articles),
                reverse=True,
            )
            if article["slug"] not in {item["slug"] for item in preferred}
        ]
        ranked_articles = preferred + remaining
        topic_cards.append(render_topic_card(category, ranked_articles, total_count))

    if secondary_categories:
        topic_cards.append(
            render_other_topics_card(
                [
                    (
                        category,
                        total_count,
                        [article for article in ordered if article["category"] == category],
                    )
                    for category, total_count in secondary_categories
                ]
            )
        )

    topic_cards_html = "\n".join(topic_cards)

    tag_map: dict[str, list[dict]] = {}
    for article in ordered:
        for tag in article["tags"]:
            tag_map.setdefault(tag, []).append(article)

    tag_counts = sorted(
        ((tag, len(tag_articles)) for tag, tag_articles in tag_map.items()),
        key=lambda item: (-item[1], item[0]),
    )

    tag_cards: list[str] = []
    primary_tags = tag_counts[:8]
    secondary_tags = tag_counts[8:]

    for tag, total_count in primary_tags:
        tag_articles = tag_map[tag]
        ranked_articles = sorted(
            tag_articles,
            key=lambda item: (item["date"], item["page_title"]),
            reverse=True,
        )
        tag_cards.append(render_topic_card(f"#{tag}", ranked_articles, total_count))

    if secondary_tags:
        tag_cards.append(
            render_other_topics_card(
                [
                    (
                        f"#{tag}",
                        count,
                        sorted(tag_map[tag], key=lambda item: (item["date"], item["page_title"]), reverse=True),
                    )
                    for tag, count in secondary_tags
                ]
            )
        )

    tag_cards_html = "\n".join(tag_cards)

    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>บทความ</title>
  <meta name="description" content="บทความและข้อเขียนประกอบวิสัยทัศน์การขับเคลื่อนมหาวิทยาลัยเกษตรศาสตร์">
{render_seo_meta(
    title="บทความ",
    description="บทความและข้อเขียนประกอบวิสัยทัศน์การขับเคลื่อนมหาวิทยาลัยเกษตรศาสตร์",
    canonical_path="articles.html",
    site_config=site_config,
)}
{render_webpage_json_ld(
    title="บทความ",
    description="บทความและข้อเขียนประกอบวิสัยทัศน์การขับเคลื่อนมหาวิทยาลัยเกษตรศาสตร์",
    canonical_path="articles.html",
    site_config=site_config,
)}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/articles-index.css">
</head>
<body>
  <main class="page">
    <section class="frame">
      <div class="inner">
        <header class="topbar">
          <div class="site-label">Kasetsart University -- The Life Systems University</div>
          <nav class="nav">
            <a href="context.html">บริบท</a>
            <a href="roles.html">บทบาท</a>
            <a href="goals.html">เป้าหมาย</a>
            <a href="strategy.html">กลยุทธ์</a>
            <a href="four-year-plan.html">แผนสี่ปี</a>
            <a href="articles.html" aria-current="page">บทความ</a>
            <a href="qa.html">ถาม/ตอบ</a>
            <a href="about.html">แนะนำตัว</a>
          </nav>
        </header>

        <section class="hero">
          <div class="hero-kicker">บทความ</div>
          <h1>Articles</h1>
          <div class="hero-subtitle">
            พื้นที่สำหรับรวบรวมบทความ ข้อเขียน และเนื้อหาด้านการศึกษา งานวิจัย และ AI
            โดย รศ.ดร.พันธุ์ปิติ เปี่ยมสง่า ซึ่งเผยแพร่ผ่าน Facebook และนำมารวบรวมไว้ที่นี่
            เพื่อประกอบการนำเสนอวิสัยทัศน์ ขยายประเด็นสำคัญให้ลึกขึ้น
            และเชื่อมโยงกับทิศทางการขับเคลื่อนมหาวิทยาลัยเกษตรศาสตร์
          </div>
          <section class="search-panel" data-archive-search>
            <div class="search-card">
              <label class="search-label" for="article-search">ค้นหาบทความ</label>
              <div class="search-helper">พิมพ์ชื่อเรื่อง หมวด หรือ tag แล้วเลือกจาก dropdown ได้ทันที</div>
              <div class="search-shell">
                <input id="article-search" class="search-input" type="search" placeholder="เช่น AI, หลักสูตร, TOI-Zero" autocomplete="off" aria-expanded="false" aria-controls="article-search-suggestions">
                <div id="article-search-suggestions" class="search-suggestions" data-search-suggestions hidden></div>
              </div>
            </div>
          </section>
          <section class="browse-entry">
            <a class="browse-entry__card" href="article-browsing.html">
              <div class="browse-entry__kicker">Browse View</div>
              <div class="browse-entry__title">เปิดหน้า Article Browsing</div>
              <div class="browse-entry__body">ดูบทความทั้งหมดแบบภาพสี่เหลี่ยมเรียงเต็มหน้า เหมาะกับการกวาดดูจากภาพก่อนเลือกอ่าน</div>
            </a>
          </section>

          <section class="content-section">
            <div class="section-heading">
              <div class="section-kicker">Featured article</div>
              <h2>บทความเด่น</h2>
            </div>
            <a class="feature-card" href="articles/{featured_article["slug"]}.html">
              <div class="feature-card__media">
                <img class="feature-card__image" src="{html.escape(featured_article["image_index"])}" alt="{html.escape(featured_article["image_alt"])}">
              </div>
              <div class="feature-card__body">
                <div class="archive-meta">{html.escape(featured_article["category"])} • {format_display_date(featured_article["date"])}</div>
                <h3>{html.escape(featured_article["page_title"])}</h3>
                <p>{featured_article["summary"]}</p>
                <div class="tag-row">
{render_tags(featured_article["tags"])}
                </div>
              </div>
            </a>
          </section>

          <section class="content-section">
            <div class="section-heading">
              <div class="section-kicker">Latest</div>
              <h2>บทความล่าสุด</h2>
            </div>
            <div class="latest-grid" data-latest-grid>
{latest_html}
{latest_extra_html}
            </div>
            <div class="section-actions">
              <div class="action-group"{" hidden" if not latest_extra else ""}>
                <button class="expand-button" type="button" data-latest-expand>ดูเพิ่ม</button>
                <button class="expand-button" type="button" data-latest-less disabled>ดูน้อยลง</button>
                <button class="expand-button" type="button" data-latest-collapse disabled>ย่อทั้งหมด</button>
              </div>
            </div>
          </section>

{render_interest_card("หัวข้อที่สนใจ", "เรียงจากจำนวนบทความมากไปน้อย และในแต่ละหมวดจะแสดง 3 เรื่องเด่นก่อน", topic_cards_html)}

{render_interest_card("แท็กที่ใช้บ่อย", "จัดกลุ่มจาก tag ที่ใช้บ่อยที่สุด เพื่อให้เห็นประเด็นย่อยที่เขียนซ้ำข้ามหลายหมวด", tag_cards_html)}
        </section>

        <footer class="footer">
          <div>Articles</div>
          <div>วิสัยทัศน์ของ รองศาสตราจารย์ ดร.พันธุ์ปิติ เปี่ยมสง่า สำหรับการสรรหาอธิการบดีมหาวิทยาลัยเกษตรศาสตร์</div>
        </footer>
      </div>
    </section>
  </main>
  <script src="assets/release-gate.js" defer></script>
  <script src="assets/site-analytics.js" defer></script>
  <script src="assets/articles-data.js" defer></script>
  <script src="assets/articles-index.js" defer></script>
</body>
</html>
"""


def render_article_browsing_page(articles: list[dict], site_config: dict) -> str:
    ordered = sorted(articles, key=lambda article: article["date"], reverse=True)
    tiles_html = "\n".join(render_browsing_tile(article) for article in ordered)
    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Article Browsing</title>
  <meta name="description" content="หน้า browse บทความแบบเต็มพื้นที่ เรียงภาพเป็น tile เพื่อสำรวจข้อเขียนทั้งหมดอย่างรวดเร็ว">
{render_seo_meta(
    title="Article Browsing",
    description="หน้า browse บทความแบบเต็มพื้นที่ เรียงภาพเป็น tile เพื่อสำรวจข้อเขียนทั้งหมดอย่างรวดเร็ว",
    canonical_path="article-browsing.html",
    site_config=site_config,
)}
{render_webpage_json_ld(
    title="Article Browsing",
    description="หน้า browse บทความแบบเต็มพื้นที่ เรียงภาพเป็น tile เพื่อสำรวจข้อเขียนทั้งหมดอย่างรวดเร็ว",
    canonical_path="article-browsing.html",
    site_config=site_config,
)}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/article-browsing.css">
</head>
<body>
  <header class="browse-topbar">
    <div class="browse-topbar__brand">Kasetsart University -- The Life Systems University</div>
    <nav class="browse-topbar__nav" aria-label="Primary">
      <a href="context.html">บริบท</a>
      <a href="roles.html">บทบาท</a>
      <a href="goals.html">เป้าหมาย</a>
      <a href="strategy.html">กลยุทธ์</a>
      <a href="four-year-plan.html">แผนสี่ปี</a>
      <a href="articles.html">บทความ</a>
      <a href="qa.html">ถาม/ตอบ</a>
      <a href="article-browsing.html" aria-current="page">Article Browsing</a>
      <a href="about.html">แนะนำตัว</a>
    </nav>
  </header>
  <main class="browse-page">
    <section class="browse-hero">
      <div class="browse-hero__kicker">Full-bleed archive view</div>
      <h1>Article Browsing</h1>
      <p>สำรวจบทความทั้งหมดผ่านภาพเต็ม tile แบบสี่เหลี่ยมจัตุรัส เพื่อกวาดดูภาพรวมได้เร็วขึ้น</p>
    </section>
    <section class="browse-grid" aria-label="Article Browsing Grid">
{tiles_html}
    </section>
  </main>
  <script src="assets/release-gate.js" defer></script>
  <script src="assets/site-analytics.js" defer></script>
</body>
</html>
"""


def main() -> None:
    articles = load_articles()
    archive_config = load_archive_config()
    site_config = load_site_config()
    validate_articles(articles)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    for article in articles:
        output = ARTICLES_DIR / f"{article['slug']}.html"
        output.write_text(render_article_page(article, site_config), encoding="utf-8")

    (DOCS_DIR / "articles.html").write_text(render_articles_index(articles, archive_config, site_config), encoding="utf-8")
    (DOCS_DIR / "article-browsing.html").write_text(render_article_browsing_page(articles, site_config), encoding="utf-8")
    (ASSETS_DIR / "articles-data.js").write_text(build_related_data(articles), encoding="utf-8")
    (ASSETS_DIR / "site-analytics.js").write_text(build_site_analytics(site_config), encoding="utf-8")
    (DOCS_DIR / "sitemap.xml").write_text(build_sitemap(articles, site_config), encoding="utf-8")
    (DOCS_DIR / "robots.txt").write_text(build_robots_txt(site_config), encoding="utf-8")


if __name__ == "__main__":
    main()
