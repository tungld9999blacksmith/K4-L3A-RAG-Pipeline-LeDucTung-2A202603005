"""
Task 2 — Crawl bài viết/thông báo tin tức.

Hướng dẫn:
    1. Đọc danh sách bài viết từ acquisition/docs/metadata.json (document_type == "news").
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
"""

import argparse
import asyncio
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List
import unicodedata

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from crawl4ai import AsyncWebCrawler


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
METADATA_FILE = Path(__file__).parent.parent / "acquisition" / "docs" / "metadata.json"


def slugify(value: str) -> str:
    """Chuyển tiêu đề thành tên file ASCII, an toàn cho hệ điều hành."""
    value = value.replace("đ", "d").replace("Đ", "d")
    normalized = unicodedata.normalize("NFKD", value)
    without_diacritics = normalized.encode("ascii", "ignore").decode("ascii")
    filename = re.sub(r"[^a-zA-Z0-9]+", "_", without_diacritics).strip("_").lower()
    if not filename:
        raise ValueError(f"Cannot create a filename from title: {value!r}")
    return filename


def setup_directory() -> None:
    """Tạo thư mục lưu tin tức dạng JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def get_news_sources() -> List[Dict[str, Any]]:
    """Đọc metadata và trả về danh sách các tài liệu có document_type == 'news'."""
    if not METADATA_FILE.exists():
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")

    with METADATA_FILE.open("r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    news_sources = [
        item for item in metadata
        if item.get("document_type") == "news" and item.get("url")
    ]
    return news_sources


# Nạp danh sách URL từ metadata.json để tương thích ngược
try:
    ARTICLE_URLS = [item["url"] for item in get_news_sources()]
except Exception:
    ARTICLE_URLS = []


def print_link_sources() -> None:
    """In các URL nguồn tin tức tương ứng trong metadata."""
    sources = get_news_sources()
    if not sources:
        raise ValueError(f"No news sources found in {METADATA_FILE}")

    for item in sources:
        filename = f"{slugify(item['title'])}.json"
        print(f"{filename}: {item['url']}")


async def crawl_article(url: str, default_title: str = "", extra_meta: Dict[str, Any] | None = None) -> dict:
    """Crawl một bài viết bằng Crawl4AI và trả về dictionary chuẩn."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if not result.success:
            raise RuntimeError(f"Crawl failed for {url}")

        crawled_title = result.metadata.get("title") if result.metadata else None
        title = default_title or crawled_title or "Unknown"
        markdown_content = result.markdown or ""

        # Nếu markdown quá ngắn hoặc rỗng, fallback sang text thông thường
        if not markdown_content.strip() and hasattr(result, "cleaned_html"):
            markdown_content = result.cleaned_html or ""

        article_data = {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": markdown_content,
        }

        # Lưu kèm thông tin metadata nếu có
        if extra_meta:
            for key in ("location", "category", "source_authority", "language"):
                if key in extra_meta:
                    article_data[key] = extra_meta[key]

        return article_data


async def crawl_all() -> None:
    """Crawl tất cả bài viết từ metadata.json và lưu thành từng file JSON."""
    setup_directory()
    sources = get_news_sources()

    if not sources:
        raise ValueError(f"No news sources found in {METADATA_FILE}")

    print(f"Bắt đầu crawl {len(sources)} bài viết...")

    for index, item in enumerate(sources, 1):
        url = item["url"]
        title = item.get("title", f"news_{index}")
        filename = f"{slugify(title)}.json"
        output_file = DATA_DIR / filename

        print(f"[{index}/{len(sources)}] Crawling: {title} ({url})")
        try:
            article = await crawl_article(url=url, default_title=title, extra_meta=item)
            output_file.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  -> Đã lưu: {output_file} ({len(article['content_markdown'])} chars)")
        except Exception as error:
            print(f"  -> Thất bại: {url} — {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Thu thập bài viết tin tức từ metadata bằng Crawl4AI.")
    parser.add_argument(
        "--print-link-source",
        action="store_true",
        help="Chỉ in tên file và URL nguồn, không crawl bài viết.",
    )
    args = parser.parse_args()

    if args.print_link_source:
        print_link_sources()
    else:
        asyncio.run(crawl_all())


if __name__ == "__main__":
    main()
