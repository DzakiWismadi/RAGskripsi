import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


class BM25Retriever:
    def __init__(self, documents: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = documents
        self.tokenized_docs = [tokenize(doc) for doc in documents]
        self.doc_lens = [len(doc) for doc in self.tokenized_docs]
        self.avg_doc_len = sum(self.doc_lens) / max(len(self.doc_lens), 1)
        self.doc_freq = self._compute_doc_freq()
        self.idf = self._compute_idf()
        self.term_freqs = [Counter(doc) for doc in self.tokenized_docs]

    def _compute_doc_freq(self) -> dict[str, int]:
        doc_freq: dict[str, int] = {}
        for doc in self.tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                doc_freq[term] = doc_freq.get(term, 0) + 1
        return doc_freq

    def _compute_idf(self) -> dict[str, float]:
        n_docs = len(self.tokenized_docs)
        idf: dict[str, float] = {}
        for term, freq in self.doc_freq.items():
            idf[term] = math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))
        return idf

    def score_query(self, query: str) -> list[float]:
        query_terms = tokenize(query)
        scores: list[float] = []

        for idx, tf_doc in enumerate(self.term_freqs):
            score = 0.0
            doc_len = self.doc_lens[idx]
            denom_norm = self.k1 * (1 - self.b + self.b * doc_len / max(self.avg_doc_len, 1e-9))
            for term in query_terms:
                if term not in tf_doc:
                    continue
                tf = tf_doc[term]
                term_idf = self.idf.get(term, 0.0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + denom_norm
                score += term_idf * (numerator / max(denominator, 1e-9))
            scores.append(score)
        return scores

