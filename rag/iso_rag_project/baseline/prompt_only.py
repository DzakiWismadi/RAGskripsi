# baseline/prompt_only.py
# Prompt-only LLM classification (no retrieval)
# Phase 3: Baseline sanity check

import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from llm.llm_wrapper import query_llm, query_llm_raw

PROMPT_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "llm", "prompt_template.txt")


def load_prompt_template() -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_baseline_prompt(sentence: str) -> str:
    """Build prompt for baseline (no retrieval context)."""
    template = load_prompt_template()
    return f"""{template}

Kalimat audit:
"{sentence}"

Jawab dalam format JSON:"""


def run_prompt_only(sentence: str) -> dict:
    """
    Run prompt-only classification (no retrieval).

    Args:
        sentence: Audit finding sentence in Indonesian.

    Returns:
        Dict with control_id, applicable, implementation_status,
        justification, recommendation.
    """
    prompt = build_baseline_prompt(sentence)
    return query_llm(prompt)


def run_prompt_only_raw(sentence: str) -> tuple[dict | None, str, float]:
    """Like run_prompt_only but returns (parsed_dict_or_None, raw_text, elapsed)."""
    prompt = build_baseline_prompt(sentence)
    return query_llm_raw(prompt)


def main():
    print("=" * 60)
    print("  Phase 3: Baseline — Prompt-Only LLM")
    print("  Tanpa retrieval, langsung ke LLM.")
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

        print("Mengirim ke LLM (tanpa retrieval)...")
        result, raw, elapsed = run_prompt_only_raw(sentence)

        print(f"\n--- Hasil Baseline (waktu: {elapsed:.2f}s) ---")
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
