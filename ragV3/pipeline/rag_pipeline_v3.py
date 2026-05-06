import sys
import time
from pathlib import Path
from typing import Any

import requests

V3_ROOT = Path(__file__).resolve().parents[1]
V1_ROOT = V3_ROOT.parent / "ragV1"

if str(V1_ROOT) not in sys.path:
    sys.path.insert(0, str(V1_ROOT))

from hybrid.hybrid_retriever import HybridRetriever
from llm.llm_wrapper import generate_answer
from reranking.cross_encoder_reranker import rerank_documents

# ── Candidate-pool & reranking defaults ──────────────────────────────────────
# Hybrid retrieval fetches CANDIDATE_POOL_SIZE docs, then the cross-encoder
# reranks them and we keep only the top-k for downstream consumption.
CANDIDATE_POOL_SIZE = 10   # broad candidate pool for reranker (10 = same perf as 20, faster)
DEFAULT_TOP_K = 3          # final output size after reranking


class RAGPipelineV3:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or V3_ROOT
        controls_path = V1_ROOT / "data" / "iso_controls_enriched.json"
        self.prompt_path = V1_ROOT / "prompts" / "prompt_template.txt"
        self.retriever = HybridRetriever(controls_path=controls_path)

    def _load_prompt_template(self) -> str:
        return self.prompt_path.read_text(encoding="utf-8").strip()

    def _format_context(self, reranked_results: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for idx, item in enumerate(reranked_results, start=1):
            lines.append(
                f"{idx}. {item['control_id']} - {item['title']} | "
                f"combined={item.get('combined_score', 0.0):.4f}, "
                f"ce={item.get('rerank_score', 0.0):.4f}, hybrid={item.get('hybrid_score', 0.0):.4f}"
            )
            lines.append(f"   Objective: {item['objective']}")
            lines.append(f"   Description: {item['description'][:220]}...")
        return "\n".join(lines)

    def build_prompt(self, query: str, reranked_results: list[dict[str, Any]]) -> str:
        template = self._load_prompt_template()
        context = self._format_context(reranked_results)
        return (
            f"{template}\n\n"
            f"Konteks kontrol ISO hasil hybrid retrieval + cross-encoder reranking (top-k):\n{context}\n\n"
            f"Pertanyaan audit:\n\"{query}\"\n\n"
            f"Jawab hanya dalam satu JSON object."
        )

    def run(
        self,
        query: str,
        k: int = DEFAULT_TOP_K,
        candidate_pool: int | None = None,
        alpha_dense: float | None = None,
        alpha_sparse: float | None = None,
        alpha_ce: float | None = None,
    ) -> dict[str, Any]:
        _pool = candidate_pool if candidate_pool is not None else CANDIDATE_POOL_SIZE

        # ── Stage 1: Broad hybrid retrieval ──────────────────────────────────
        retrieval_start = time.perf_counter()
        retrieval = self.retriever.retrieve(
            query=query, k=_pool, method_order=["hybrid"],
            dense_weight=alpha_dense, sparse_weight=alpha_sparse,
        )
        retrieval_time = time.perf_counter() - retrieval_start

        retrieved_docs = retrieval.get("hybrid_results", [])

        # ── Stage 2: Cross-encoder reranking ─────────────────────────────────
        reranking_start = time.perf_counter()
        reranked_docs = rerank_documents(
            query=query, retrieved_docs=retrieved_docs, top_n=k,
            alpha=alpha_ce,
        )
        reranking_time = time.perf_counter() - reranking_start

        total_time = retrieval_time + reranking_time
        prompt = self.build_prompt(query=query, reranked_results=reranked_docs)

        llm_error = None
        llm_model = "qwen2.5:3b"
        answer: Any
        try:
            llm_result = generate_answer(prompt)
            llm_model = llm_result["model"]
            answer = llm_result["parsed_json"] if llm_result["parsed_json"] is not None else llm_result["raw_text"]
        except requests.RequestException as exc:
            llm_error = f"LLM request failed: {exc}"
            answer = {"error": llm_error}

        effective_alpha_dense = alpha_dense if alpha_dense is not None else 0.6
        effective_alpha_sparse = alpha_sparse if alpha_sparse is not None else 0.4
        effective_alpha_ce = alpha_ce if alpha_ce is not None else 0.8
        effective_pool = candidate_pool if candidate_pool is not None else CANDIDATE_POOL_SIZE

        return {
            "query": query,
            "hybrid_results": retrieved_docs,
            "reranked_results": reranked_docs,
            "answer": answer,
            "llm_model": llm_model,
            "llm_error": llm_error,
            "fusion": retrieval.get("fusion", {"method": "weighted_sum", "dense_weight": 0.6, "sparse_weight": 0.4}),
            "timings": {
                "retrieval_time": float(retrieval_time),
                "reranking_time": float(reranking_time),
                "total_time": float(total_time),
            },
            "params": {
                "alpha_dense": effective_alpha_dense,
                "alpha_sparse": effective_alpha_sparse,
                "alpha_ce": effective_alpha_ce,
                "candidate_pool": effective_pool,
                "k": k,
            },
        }

