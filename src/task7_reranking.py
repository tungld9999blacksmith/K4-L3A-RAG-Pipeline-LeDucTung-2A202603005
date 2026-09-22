"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""

import numpy as np

from typing import Tuple

def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    # TODO: Implement RRF.
    #

    doc_ids = {item["id"] for ranked_list in ranked_lists for item in ranked_list}

    n_doc = len(doc_ids)

    doc2idx = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}

    idx2doc = {idx: doc_id for doc_id, idx in doc2idx.items()}

    ranked_tensors = np.zeros((len(ranked_lists), len(doc_ids)), dtype = np.float64) # #shape = (#metrics x #docs)

    doc_indicies = []
    metric_indicies = []

    ranks_in_metric = []

    # flattening indexes for vectorzing computation
    for metric_id in range(len(ranked_lists)):

        n_doc = len(ranked_lists[metric_id])

        doc_indicies.extend([doc2idx[item["id"]] for item in ranked_lists[metric_id]])

        metric_indicies.extend([metric_id] * n_doc)

        ranks_in_metric.extend(range(1, n_doc + 1))
    
    
    doc_indicies = np.array(doc_indicies, dtype = np.intp)
    metric_indicies = np.array(metric_indicies, dtype = np.intp)
    ranks_in_metric = np.array(ranks_in_metric, dtype = np.float64)

    ranked_tensors[metric_indicies, doc_indicies] = 1.0 / (k + ranks_in_metric)

    sum_tensors = ranked_tensors.sum(axis = 0)

    if top_k < n_doc:
        top_k_indicies = np.argpartition(sum_tensors, -top_k)[-top_k:]
        top_k_indicies = top_k_indicies[np.argsort(-sum_tensors[top_k_indicies])]
    else:
        top_k_indicies = np.argsort(-sum_tensors)

    def retrieve_remain_fields(idx: str) -> Tuple[str, dict]:
        for ranked_row in ranked_lists:
            for item in ranked_row:
                if item["id"] == idx2doc[idx]:
                    return item["content"], item["metadata"]
        return "", {}

    remain_content = {doc_id: retrieve_remain_fields(doc_id) for doc_id in top_k_indicies}

    results = [
        {
            "id": idx2doc[item_id],
            "score": sum_tensors[item_id],
            "retrieval_method": "hybrid",
            "content": remain_content[item_id][0],
            "metadata": remain_content[item_id][1],
        }
        for item_id in top_k_indicies
    ]
    return results


if __name__ == "__main__":
    print("Implement rerank_rrf, then run contract tests.")
