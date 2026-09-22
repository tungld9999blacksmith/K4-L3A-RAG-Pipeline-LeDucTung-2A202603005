"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict
import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
METADATA_FILE = Path(__file__).parent.parent / "acquisition" / "docs" / "metadata.json"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    sources = get_document_sources()

    if not sources:
        raise ValueError(f"No PDF/DOCX sources found in {METADATA_FILE}")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for filename, url in sources.items():
        output_file = DATA_DIR / filename
        if output_file.exists():
            print(f"Already exists, skipping: {output_file}")
            continue
        print(f"Downloading: {filename} <- {url}")
        try:
            response = requests.get(url, timeout=60, headers=headers)
            response.raise_for_status()
            output_file.write_bytes(response.content)
            print(f"Downloaded: {output_file}")
        except Exception as err:
            print(f"  -> Lỗi tải {filename}: {err}")


_DOCTYPE_EXT = {
    "factual_pdf": ".pdf",
    "factual_docx": ".docx",
}


def get_document_sources() -> Dict[str, str]:
    """Đọc metadata và trả về ánh xạ tên file tải về với URL nguồn."""
    with METADATA_FILE.open("r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    sources: Dict[str, str] = {}
    for document in metadata:
        url = document.get("url", "")
        document_type = document.get("document_type", "")

        if document_type not in _DOCTYPE_EXT:
            continue

        # Lấy extension từ URL; nếu không có thì fallback theo document_type
        url_ext = Path(url.split("?", maxsplit=1)[0]).suffix.lower()
        extension = url_ext if url_ext in {".pdf", ".docx"} else _DOCTYPE_EXT[document_type]

        filename = f"{slugify(document['title'])}{extension}"
        sources.setdefault(filename, url)

    return sources


def print_link_sources() -> None:
    """In các URL nguồn tương ứng với tài liệu PDF/DOCX trong metadata."""
    sources = get_document_sources()
    if not sources:
        raise ValueError(f"No PDF/DOCX sources found in {METADATA_FILE}")

    for filename, url in sources.items():
        print(f"{filename}: {url}")


def slugify(value: str) -> str:
    """Chuyển tiêu đề thành tên file ASCII, an toàn cho hệ điều hành."""
    normalized = unicodedata.normalize("NFKD", value)
    without_diacritics = normalized.encode("ascii", "ignore").decode("ascii")
    filename = re.sub(r"[^a-zA-Z0-9]+", "_", without_diacritics).strip("_").lower()
    if not filename:
        raise ValueError(f"Cannot create a filename from title: {value!r}")
    return filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thu thập tài liệu pháp lý từ metadata.")
    parser.add_argument(
        "--print-link-source",
        action="store_true",
        help="Chỉ in tên file và URL nguồn, không tải tài liệu.",
    )
    args = parser.parse_args()

    if args.print_link_source:
        print_link_sources()
    else:
        setup_directory()
        download_documents()
