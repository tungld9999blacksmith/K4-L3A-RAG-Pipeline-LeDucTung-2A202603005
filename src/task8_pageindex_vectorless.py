"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

CACHE_PATH = Path(__file__).parent.parent / "pageindex_cache.json"

SUPPORTED_SUFFIXES = {".pdf", ".doc", "docx"}

def _setup_pageindex_client() -> PageIndexClient:

    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY is not configured in .env")
    
    from pageindex import PageIndexClient

    return PageIndexClient(api_key=PAGEINDEX_API_KEY)


def _load_cache() -> dict[str, str]:
    """Load cache map source -> doc_id."""
    if not CACHE_PATH.exists():
        return {}
    
    return json.load(CACHE_PATH)


def _save_cache(cache: dict[str, str]) -> None:
    """Save cache."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    # TODO: Upload documents và lưu mapping source -> document ID.
    #
    # Nếu SDK không nhận Markdown, convert sang PDF tạm trước khi upload.
    # Kiểm tra response thật của SDK thay vì đoán tên field.
    page_idx_client = _setup_pageindex_client()
    cache = _load_cache()

    landing_dir = Path(__file__).parent.parent / "data" / "landing" / "legal"

    for path in sorted(landing_dir.iterdir()):
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        
        source = path.name
        if source in cache:
            logger.info(f"Document {source} already uploaded (ID: {cache[source]}). Skipping.")
            continue
        
        response = client.submit_document(file_path = str(path))
        doc_id = response.get("id") or response.get("doc_id")

        if not doc_id:
            print(f"Cannot retrieve the document id for {path.name}: {response}")
            continue

        cache[path.name] = doc_id
        print(f"Uploaded: {path.name} -> {doc_id}")
    
    _save_cache(cache)


def _extract_content(response: dict) -> str:

    if not isinstance(response, dict):
        return ""
    
    for key in ("content", "answer", "text", "response"):
        value = response.get(key, None)

        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""



def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    # TODO: Query các document IDs và parse retrieved nodes.
    #
    # Mỗi result cần: id, content, score, metadata, retrieval_method.
    # Nếu API không trả score, có thể gán score giảm dần theo rank.
    if top_k <= 0:
        return []
    
    cache = _load_cache()

    if not cache:
        raise RuntimeError("Cannot exists any uploaded documents. Please run upload_documents() first")
    
    page_idx_client: PageIndexClient = _setup_pageindex_client()

    doc_ids = list(cache.values())

    results: list[dict] = []

    for source, doc_id in cache.items():
        if len(results) >= top_k:
            break

        if not page_idx_client.is_retrieval_ready(doc_id=doc_id):
            print(f"Document {doc_id} is not ready for retrieval. Skipping.")
            continue

        response = client.submit_query(doc_id = doc_id, query=query)

        content = _extract_content(response)

        if not content:
            continue

        metadata = {
            "source": source,
            "title": Path(source).stem,
            "doc_type": "legal",
            "url": "",
            "chunk_index": len(results),
        }
        results.append(
            {
                "id": f"pageindex::{doc_id}::{len(results)}",
                "content": content,
                "score": 0.0,
                "metadata": metadata,
                "retrieval_method": "pageindex",
            }
        )
    total = len(results)

    for index, result in enumerate(results):
        result["score"] = float(total-index)
    return results

       


                
        


if __name__ == "__main__":
    upload_documents()
