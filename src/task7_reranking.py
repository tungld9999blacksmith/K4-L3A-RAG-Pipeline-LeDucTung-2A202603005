"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""

import numpy as np

def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    # TODO: Implement RRF.
    #

    doc_idx = set([item["id"] for ranked_list in ranked_lists for item in ranked_list])
    doc2idx = {doc_id: idx for idx, doc_id in enumerate(doc_idx)}

    idx2doc = {idx: doc_id for doc_id, idx in doc2idx.items()}

    ranked_tensors = np.zeros((len(ranked_lists), len(doc_idx))) # #shape = (#metrics x #docs)

    for metric_id in range(len(ranked_lists)):
        for rank_of_doc, doc in enumerate(ranked_lists[metric_id], 1):
            doc_id = doc["id"]
            doc_idx_in_tensor = doc2idx[doc_id]
            ranked_tensors[metric_id, doc_idx_in_tensor] = 1 / (k + rank_of_doc)

    sum_tensors = ranked_tensors.sum(axis = 0)
    ranked_ids = np.argsort(sum_tensors)[::-1][:top_k]
    
    results = []
    for item_id in ranked_ids:
        doc_id = idx2doc[item_id]
        result = {
            "id": doc_id,
            "score": sum_tensors[item_id],
            "retrieval_method": "hybrid",
            "content": CORPUS[doc_id]["content"],
            "metadata": CORPUS[doc_id]["metadata"],
        }
        results.append(result)
    return results


if __name__ == "__main__":
    print("Implement rerank_rrf, then run contract tests.")
