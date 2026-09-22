"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX trong data/landing/legal/.
    2. Đọc JSON trong data/landing/news/ và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục standardized/legal/ và standardized/news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.
"""

import json
from pathlib import Path
from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert tài liệu PDF/DOCX từ data/landing/legal sang data/standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not legal_dir.exists():
        print(f"Thư mục không tồn tại: {legal_dir}")
        return

    converter = MarkItDown()

    for path in sorted(legal_dir.iterdir()):
        if path.name.startswith("."):
            continue
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            output_file = output_dir / f"{path.stem}.md"
            print(f"Converting legal doc: {path.name}")
            try:
                result = converter.convert(str(path))
                text_content = (result.text_content or "").strip()
                if not text_content:
                    print(f"  -> Cảnh báo: File rỗng hoặc không trích xuất được text: {path.name}")
                    continue

                output_file.write_text(text_content, encoding="utf-8")
                print(f"  -> Đã lưu: {output_file} ({len(text_content)} chars)")
            except Exception as e:
                print(f"  -> Lỗi convert {path.name}: {e}")


def convert_news_articles() -> None:
    """Convert tin tức dạng JSON từ data/landing/news sang data/standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not news_dir.exists():
        print(f"Thư mục không tồn tại: {news_dir}")
        return

    for path in sorted(news_dir.glob("*.json")):
        if path.name.startswith("."):
            continue

        output_file = output_dir / f"{path.stem}.md"
        print(f"Converting news JSON: {path.name}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            title = data.get("title", path.stem)
            url = data.get("url", "")
            date_crawled = data.get("date_crawled", "")
            content = data.get("content_markdown", "").strip()

            header_lines = [
                f"# {title}",
                "",
                f"**Source:** {url}",
                "",
                f"**Crawled:** {date_crawled}",
            ]

            if data.get("location"):
                header_lines.extend(["", f"**Location:** {data['location']}"])
            if data.get("category"):
                header_lines.extend(["", f"**Category:** {data['category']}"])
            if data.get("source_authority"):
                header_lines.extend(["", f"**Authority:** {data['source_authority']}"])

            header_lines.extend(["", "---", "", ""])
            header = "\n".join(header_lines)

            markdown_full = header + content
            if not content:
                print(f"  -> Cảnh báo: Nội dung news rỗng: {path.name}")
                continue

            output_file.write_text(markdown_full, encoding="utf-8")
            print(f"  -> Đã lưu: {output_file} ({len(markdown_full)} chars)")
        except Exception as e:
            print(f"  -> Lỗi convert {path.name}: {e}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu từ landing sang standardized."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Hoàn thành chuyển đổi. Thư mục đầu ra: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
