import json
import time
from pathlib import Path

import numpy as np

from dense.embedding_model import control_to_text, encode_texts
from sparse.bm25 import BM25Retriever

DENSE_WEIGHT = 0.6
SPARSE_WEIGHT = 0.4
VALID_METHODS = ("dense", "sparse", "hybrid")


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

    @staticmethod
    def _normalize_method_order(method_order: list[str] | tuple[str, ...] | None) -> list[str]:
        order = list(method_order or VALID_METHODS)
        lowered = [str(name).strip().lower() for name in order]
        if not lowered:
            raise ValueError(f"method_order must contain at least one of: {', '.join(VALID_METHODS)}")
        if any(name not in VALID_METHODS for name in lowered):
            raise ValueError(f"method_order can only contain: {', '.join(VALID_METHODS)}")
        if len(set(lowered)) != len(lowered):
            raise ValueError("method_order must not contain duplicate methods")
        return lowered

    def retrieve(self, query: str, k: int = 3, method_order: list[str] | tuple[str, ...] | None = None, dense_weight: float | None = None, sparse_weight: float | None = None) -> dict:
        order = self._normalize_method_order(method_order)
        _dw = dense_weight if dense_weight is not None else DENSE_WEIGHT
        _sw = sparse_weight if sparse_weight is not None else SPARSE_WEIGHT
        dense_scores: np.ndarray | None = None
        sparse_scores: np.ndarray | None = None
        hybrid_scores: np.ndarray | None = None
        dense_time = 0.0
        sparse_time = 0.0
        hybrid_time = 0.0

        def ensure_dense() -> None:
            nonlocal dense_scores, dense_time
            if dense_scores is not None:
                return
            print("[EVALUATION] Running method: dense")
            start = time.perf_counter()
            dense_scores = self._dense_scores(query)
            dense_time = time.perf_counter() - start

        def ensure_sparse() -> None:
            nonlocal sparse_scores, sparse_time
            if sparse_scores is not None:
                return
            print("[EVALUATION] Running method: sparse")
            start = time.perf_counter()
            sparse_scores = np.array(self.bm25.score_query(query), dtype=np.float32)
            sparse_time = time.perf_counter() - start

        def ensure_hybrid() -> None:
            nonlocal dense_scores, sparse_scores, hybrid_scores, hybrid_time
            if hybrid_scores is not None:
                return
            print("[EVALUATION] Running method: hybrid")
            start = time.perf_counter()
            dense_for_hybrid = self._dense_scores(query)
            sparse_for_hybrid = np.array(self.bm25.score_query(query), dtype=np.float32)
            dense_norm = self._minmax(dense_for_hybrid.tolist())
            sparse_norm = self._minmax(sparse_for_hybrid.tolist())
            hybrid_scores = _dw * dense_norm + _sw * sparse_norm
            hybrid_time = time.perf_counter() - start
            if dense_scores is None:
                dense_scores = dense_for_hybrid
            if sparse_scores is None:
                sparse_scores = sparse_for_hybrid

        executors = {"dense": ensure_dense, "sparse": ensure_sparse, "hybrid": ensure_hybrid}
        for method_name in order:
            executors[method_name]()

        total_docs = len(self.controls)
        zero_scores = np.zeros(total_docs, dtype=np.float32)
        dense_scores_for_build = dense_scores if dense_scores is not None else zero_scores
        sparse_scores_for_build = sparse_scores if sparse_scores is not None else zero_scores
        hybrid_scores_for_build = hybrid_scores if hybrid_scores is not None else zero_scores

        dense_results: list[dict] = []
        sparse_results: list[dict] = []
        hybrid_results: list[dict] = []
        if "dense" in order and dense_scores is not None:
            dense_rank = np.argsort(-dense_scores)[:k]
            dense_results = [
                self._build_result(i, float(dense_scores_for_build[i]), float(sparse_scores_for_build[i]), float(hybrid_scores_for_build[i]))
                for i in dense_rank
            ]
        if "sparse" in order and sparse_scores is not None:
            sparse_rank = np.argsort(-sparse_scores)[:k]
            sparse_results = [
                self._build_result(i, float(dense_scores_for_build[i]), float(sparse_scores_for_build[i]), float(hybrid_scores_for_build[i]))
                for i in sparse_rank
            ]
        if "hybrid" in order and hybrid_scores is not None:
            hybrid_rank = np.argsort(-hybrid_scores)[:k]
            hybrid_results = [
                self._build_result(i, float(dense_scores_for_build[i]), float(sparse_scores_for_build[i]), float(hybrid_scores_for_build[i]))
                for i in hybrid_rank
            ]

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
                "dense_weight": _dw,
                "sparse_weight": _sw,
            },
            "method_order": order,
        }

