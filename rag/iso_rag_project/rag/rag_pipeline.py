# rag/rag_pipeline.py
# Full RAG pipeline: embed -> retrieve -> inject -> LLM -> structured output
# Phase 4: RAG sanity check

import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from retrieval.retrieve import retrieve_top3, format_retrieved_for_prompt
from llm.llm_wrapper import query_llm, query_llm_raw

PROMPT_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "llm", "prompt_template.txt")


def load_prompt_template() -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_rag_prompt(sentence: str, retrieved_controls: list[dict]) -> str:
    """Build prompt with retrieved ISO controls injected as context."""
    template = load_prompt_template()
    context = format_retrieved_for_prompt(retrieved_controls)

    return f"""{template}

Berikut adalah kontrol ISO 27001 yang paling relevan berdasarkan pencarian semantik:

{context}

Gunakan HANYA kontrol di atas sebagai referensi untuk menjawab. Jangan gunakan pengetahuan di luar kontrol yang diberikan.

Kalimat audit:
"{sentence}"

Jawab dalam format JSON:"""


def run_rag(sentence: str) -> dict:
    """
    Run RAG-based classification.

    Steps:
    1. Retrieve top-3 ISO controls via FAISS
    2. Inject into prompt as context
    3. Send to LLM
    4. Parse and return structured JSON

    Args:
        sentence: Audit finding sentence in Indonesian.

    Returns:
        Dict with control_id, applicable, implementation_status,
        justification, recommendation.
    """
    retrieved = retrieve_top3(sentence)
    prompt = build_rag_prompt(sentence, retrieved)
    result = query_llm(prompt)
    result["_retrieved_controls"] = [
        {"control_id": r["control_id"], "similarity_score": r["similarity_score"]}
        for r in retrieved
    ]
    return result


def run_rag_raw(sentence: str) -> tuple[dict | None, str, float, list[dict]]:
    """
    Like run_rag but returns (parsed_dict_or_None, raw_text, elapsed, retrieved_controls).
    Does not raise on parse failure.
    """
    retrieved = retrieve_top3(sentence)
    prompt = build_rag_prompt(sentence, retrieved)
    result, raw, elapsed = query_llm_raw(prompt)
    return result, raw, elapsed, retrieved


def main():
    print("=" * 60)
    print("  Phase 4: RAG Pipeline")
    print("  Retrieval + LLM (konteks ISO 27001 diinjeksi).")
    print("  Ketik kalimat audit, lalu tekan Enter.")
    print("  Ketik 'exit' untuk keluar.")
    print("=" * 60)

    while True:
        try:
            sentence = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSampai jumpa!")
            break

        if not sentence:
            continue
        if sentence.lower() in ("exit", "quit", "q"):
            print("Sampai jumpa!")
            break

        print("Mencari kontrol relevan...")
        result, raw, elapsed, retrieved = run_rag_raw(sentence)

        print(f"\n--- Kontrol yang di-retrieve (Top-3) ---")
        for i, r in enumerate(retrieved, 1):
            print(f"  {i}. [{r['control_id']}] {r['title']} (score: {r['similarity_score']:.4f})")

        print(f"\n--- Hasil RAG (waktu: {elapsed:.2f}s) ---")
        if result:
            print(f"  control_id           : {result['control_id']}")
            print(f"  applicable           : {result['applicable']}")
            print(f"  implementation_status: {result['implementation_status']}")
            print(f"  justification        : {result['justification']}")
            print(f"  recommendation       : {result['recommendation']}")
        else:
            print(f"  GAGAL parse JSON dari respons LLM.")
            print(f"  Raw response:\n{raw}")


if __name__ == "__main__":
    main()
