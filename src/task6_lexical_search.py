"""


Task 6 — Lexical search bằng BM25.



Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài


liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.

"""



from typing import List, Set, List

import numpy as np
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

def load_corpus() -> list[dict]:
    """Đọc các tài liệu Markdown chuẩn hóa làm corpus cho BM25."""
    corpus = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        relative_path = path.relative_to(STANDARDIZED_DIR)
        doc_type = relative_path.parts[0] if relative_path.parts else "unknown"
        corpus.append({
            "id": relative_path.as_posix(),
            "content": path.read_text(encoding="utf-8"),
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": None,
                "chunk_index": 0,
            },
        })
    return corpus

CORPUS: list[dict] = load_corpus()

def naive_tokenize_document(doc: str, sep_char: str) -> np.ndarray:

    return np.array([word for word in doc.lower().split(sep_char) if word])



def naive_compute_idf_each_word(term_frequency_matrix: np.ndarray, n_documents: int, word: str) -> float:

    df = np.sum(term_frequency_matrix == word).astype(int)

    return np.log((n_documents + 1) / (df + 1))  + 1 # smooth



def naive_compute_idf(term_freq_mtx: np.ndarray, smooth: bool = False, smooth_factor = 0.5) -> np.ndarray:

    N = term_freq_mtx.shape[0]

    df = np.sum(term_freq_mtx > 0, axis=1).astype(int)
    

    if smooth:

        return np.log((N - df + smooth_factor) / (df + smooth_factor))
    else:

        return np.log((N - df) / df)
        

def naive_compute_tf(seq_of_array: list, n_vocab) -> np.ndarray:

    vocab_ids = np.arange(n_vocab)

    matches = [seq[:, None] == vocab_ids for seq in seq_of_array]

    return np.array([np.sum(match, axis= 0) for match in matches]).T # shape: (vocab_size, N_documents)


class NaiveBM25:

    def __init__(self, corpus: list[dict], sep_char = ' ', smooth = True, smooth_factor = 0.5, k1: float = 1.75, b: float = 0.75) -> None:
        self.corpus = corpus

        self.sep_char = sep_char

        self.k1 = k1

        self.b = b

        self.smooth = smooth

        self.smooth_factor = smooth_factor

        self.tokenized_corpus = None

        self.vocabulary = np.array([])

        self.word2idx = None

        self.idx2word = None

        self.tf = None

        self.idf = None

        self.dl = None

        self.avgdl = None

        self.rarerity = None

        self._preprocess()

    def _preprocess(self) -> None:

        self.tokenized_corpus = [naive_tokenize_document(doc["content"], self.sep_char) for doc in self.corpus]

        for doc in self.tokenized_corpus:
            self.vocabulary = np.union1d(self.vocabulary, np.unique(doc))

        self.word2idx = {word: idx for idx, word in enumerate(self.vocabulary)}

        self.idx2word = {idx: word for word, idx in self.word2idx.items()}

        self.tf = naive_compute_tf(self.tokenized_corpus, len(self.vocabulary))

        self.idf = naive_compute_idf(self.tf, self.smooth, self.smooth_factor)

        self.dl = np.array([len(doc) for doc in self.tokenized_corpus])

        self.avgdl = np.mean(self.dl)


        n_vocab = self.vocabulary.shape[0]

        n_document = len(self.tokenized_corpus)

        self.rarerity = np.zeros((n_vocab, n_document))

        for doc_id in range(n_document):
            for char in self.tokenized_corpus[doc_id]:
                token_id = self.word2idx[char]
                self.rarerity[token_id, doc_id] = (self.tf[token_id, doc_id] * (self.k1 +1)) / (self.tf[token_id, doc_id] + self.k1 * (1 - self.b + self.b * self.dl[doc_id] / self.avgdl))

    
    

    def compute_idx(self, query: str) -> np.ndarray:


        tokenized_query = naive_tokenize_document(query, self.sep_char)
        

        terms, freq = np.unique(tokenized_query, return_counts=True)


        valid_mask = np.array([t in self.word2idx for t in terms])


        if not np.any(valid_mask):

            return np.zeros(self.rarerity.shape[1]) 


        valid_terms = terms[valid_mask]

        valid_freq = freq[valid_mask]  # shape: (K_valid,)


        term_idx = np.array([self.word2idx[t] for t in valid_terms])


        term_weights = (valid_freq * self.idf[term_idx])[:, None] # shape: (K_valid, 1)


        rarerity = self.rarerity[term_idx] # shape: (K_valid, N_document)


        scores = np.sum(term_weights * rarerity, axis=0) # shape: (N_document,)

        return scores 


    

def build_bm25_index(corpus: list[dict]):

    """Tạo BM25 index từ cùng corpus chunks của Task 4."""

    # TODO: Tokenize và tạo BM25 index.

    #

    from rank_bm25 import BM25Okapi

    tokenized = [item["content"].lower().split() for item in corpus]

    return BM25Okapi(tokenized)



def lexical_search(query: str, top_k: int = 10) -> list[dict]:

    """Trả về BM25 SearchResult theo score giảm dần."""

    # TODO: Tính BM25 scores và map lại corpus.

    #

    #import numpy as np

    #bm25 = build_bm25_index(CORPUS)

    #scores = bm25.get_scores(query.lower().split())

    #indices = np.argsort(scores)[::-1][:top_k]


    bm25_metric = NaiveBM25(CORPUS)

    scores = bm25_metric.compute_idx(query)


    indices = np.argsort(scores)[::-1][:top_k]


    results = []

    for index in indices:

        if scores[index] <= 0:
            continue

        item = CORPUS[index]

        results.append({

            "id": item["id"],

            "content": item["content"],

            "score": float(scores[index]),

            "metadata": item["metadata"],

            "retrieval_method": "bm25",

        })
    return results



if __name__ == "__main__":

    for result in lexical_search("test query", top_k=3):
        print(result)

