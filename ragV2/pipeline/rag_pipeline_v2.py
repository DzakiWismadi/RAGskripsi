import time
from pathlib import Path
from typing import Any

import requests

from query_expansion.query_expansion import query_expansion

V1_ROOT = Path(__file__).resolve().parents[2] / "ragV1"
_CONTROLS_PATH = V1_ROOT / "data" / "iso_controls.json"

import sys
if str(V1_ROOT) not in sys.path:
    sys.path.insert(0, str(V1_ROOT))

from hybrid.hybrid_retriever import HybridRetriever
from llm.llm_wrapper import generate_answer


class RAGPipelineV2:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.prompt_path = V1_ROOT / "prompts" / "prompt_template.txt"
        self.retriever = HybridRetriever(controls_path=_CONTROLS_PATH)

    def _load_prompt_template(self) -> str:
        return self.prompt_path.read_text(encoding="utf-8").strip()

    def _format_context(self, hybrid_results: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for idx, item in enumerate(hybrid_results, start=1):
            lines.append(
                f"{idx}. {item['control_id']} - {item['title']} | "
                f"dense={item['dense_score']:.4f}, sparse={item['sparse_score']:.4f}, hybrid={item['hybrid_score']:.4f}"
            )
            lines.append(f"   Objective: {item['objective']}")
            lines.append(f"   Description: {item['description'][:220]}...")
        return "\n".join(lines)

    def build_prompt(self, query: str, hybrid_results: list[dict[str, Any]]) -> str:
        template = self._load_prompt_template()
        context = self._format_context(hybrid_results)
        return (
            f"{template}\n\n"
            f"Konteks kontrol ISO hasil retrieval hybrid (top-k):\n{context}\n\n"
            f"Pertanyaan audit:\n\"{query}\"\n\n"
            f"Jawab hanya dalam satu JSON object."
        )

    def run(self, query: str, k: int = 3) -> dict[str, Any]:
        expansion = query_expansion(query)
        expanded_query = expansion["expanded_query"]
        llm_time = expansion["llm_time"]

        retrieval = self.retriever.retrieve(query=expanded_query, k=k)
        retrieval_time = retrieval["timings"]["total_time"]

        prompt = self.build_prompt(query=query, hybrid_results=retrieval["hybrid_results"])
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

        return {
            "original_query": query,
            "expanded_query": expanded_query,
            "dense_results": retrieval["dense_results"],
            "sparse_results": retrieval["sparse_results"],
            "hybrid_results": retrieval["hybrid_results"],
            "answer": answer,
            "llm_model": llm_model,
            "llm_error": llm_error,
            "fusion": retrieval["fusion"],
            "timings": {
                "llm_time": llm_time,
                "retrieval_time": retrieval_time,
                "total_time": llm_time + retrieval_time,
            },
            "method_order": retrieval["method_order"],
        }
