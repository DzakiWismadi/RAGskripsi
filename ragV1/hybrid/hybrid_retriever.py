import json
import time
from pathlib import Path

import numpy as np

from dense.embedding_model import control_to_text, encode_texts
from sparse.bm25 import BM25Retriever

DENSE_WEIGHT = 0.6
SPARSE_WEIGHT = 0.4


class HybridRetriever:
    def __init__(self, controls_path: Path):
        self.controls_path = controls_path
        self.controls = self._load_controls()
        self.control_texts = [control_to_text(c) for c in self.controls]
        self.doc_embeddings = encode_texts(self.control_texts)
        self.bm25 = BM25Retriever(self.control_texts)

    def _load_controls(self) -> list[dict]:
        with self.controls_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _minmax(scores: list[float]) -> np.ndarray:
        arr = np.array(scores, dtype=np.float32)
        min_v = float(np.min(arr))
        max_v = float(np.max(arr))
        if max_v - min_v <= 1e-12:
            return np.zeros_like(arr)
        return (arr - min_v) / (max_v - min_v)

    def _dense_scores(self, query: str) -> np.ndarray:
        q_emb = encode_texts([query])[0]
        return np.dot(self.doc_embeddings, q_emb)

    def _build_result(self, idx: int, dense_score: float, sparse_score: float, hybrid_score: float) -> dict:
        control = self.controls[idx]
        return {
            "control_id": control["control_id"],
            "title": control["title"],
            "objective": control["objective"],
            "description": control["description"],
            "dense_score": float(dense_score),
            "sparse_score": float(sparse_score),
            "hybrid_score": float(hybrid_score),
        }

    def retrieve(self, query: str, k: int = 3) -> dict:
        dense_start = time.perf_counter()
        dense_scores = self._dense_scores(query)
        dense_time = time.perf_counter() - dense_start

        sparse_start = time.perf_counter()
        sparse_scores = np.array(self.bm25.score_query(query), dtype=np.float32)
        sparse_time = time.perf_counter() - sparse_start

        hybrid_start = time.perf_counter()
        dense_norm = self._minmax(dense_scores.tolist())
        sparse_norm = self._minmax(sparse_scores.tolist())
        hybrid_scores = DENSE_WEIGHT * dense_norm + SPARSE_WEIGHT * sparse_norm

        dense_rank = np.argsort(-dense_scores)[:k]
        sparse_rank = np.argsort(-sparse_scores)[:k]
        hybrid_rank = np.argsort(-hybrid_scores)[:k]

        dense_results = [
            self._build_result(i, float(dense_scores[i]), float(sparse_scores[i]), float(hybrid_scores[i]))
            for i in dense_rank
        ]
        sparse_results = [
            self._build_result(i, float(dense_scores[i]), float(sparse_scores[i]), float(hybrid_scores[i]))
            for i in sparse_rank
        ]
        hybrid_results = [
            self._build_result(i, float(dense_scores[i]), float(sparse_scores[i]), float(hybrid_scores[i]))
            for i in hybrid_rank
        ]
        hybrid_time = time.perf_counter() - hybrid_start

        return {
            "dense_results": dense_results,
            "sparse_results": sparse_results,
            "hybrid_results": hybrid_results,
            "timings": {
                "dense_time": float(dense_time),
                "sparse_time": float(sparse_time),
                "hybrid_time": float(hybrid_time),
                "total_time": float(dense_time + sparse_time + hybrid_time),
            },
            "fusion": {
                "method": "weighted_sum",
                "dense_weight": DENSE_WEIGHT,
                "sparse_weight": SPARSE_WEIGHT,
            },
        }

