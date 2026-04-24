"""
Test script for Phase 3 (Baseline) vs Phase 4 (RAG) comparison.
Run: python test_phase3_4.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baseline.prompt_only import run_prompt_only_raw
from rag.rag_pipeline import run_rag_raw

TESTS = [
    ("Karyawan tidak pernah mendapat pelatihan keamanan informasi.", "A.6.3"),
    ("Backup data tidak pernah diuji pemulihannya.", "A.8.13"),
    ("Jaringan kantor tidak memiliki firewall dan semua perangkat berada dalam satu segmen.", "A.8.20"),
]

def main():
    print("=" * 80)
    print("PHASE 3 vs PHASE 4 - Comparison Test")
    print("=" * 80)

    results = []

    for i, (sentence, expected) in enumerate(TESTS, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}: {sentence}")
        print(f"Expected: {expected}")
        print("=" * 80)

        # Phase 3: Baseline
        print("\n[BASELINE] Mengirim ke LLM tanpa retrieval...")
        b_result, b_raw, b_time = run_prompt_only_raw(sentence)
        if b_result:
            print(f"  control_id : {b_result['control_id']}")
            print(f"  applicable : {b_result['applicable']}")
            print(f"  status     : {b_result['implementation_status']}")
            print(f"  justifikasi: {b_result['justification'][:120]}")
            print(f"  waktu      : {b_time:.2f}s")
        else:
            print(f"  GAGAL parse JSON.")
            print(f"  Raw: {b_raw[:300]}")

        # Phase 4: RAG
        print("\n[RAG] Mencari kontrol + mengirim ke LLM...")
        r_result, r_raw, r_time, retrieved = run_rag_raw(sentence)
        print(f"  Retrieved:")
        for j, rc in enumerate(retrieved, 1):
            print(f"    {j}. [{rc['control_id']}] {rc['title']} (score: {rc['similarity_score']:.4f})")
        if r_result:
            print(f"  control_id : {r_result['control_id']}")
            print(f"  applicable : {r_result['applicable']}")
            print(f"  status     : {r_result['implementation_status']}")
            print(f"  justifikasi: {r_result['justification'][:120]}")
            print(f"  waktu      : {r_time:.2f}s")
        else:
            print(f"  GAGAL parse JSON.")
            print(f"  Raw: {r_raw[:300]}")

        b_cid = b_result['control_id'] if b_result else 'FAIL'
        r_cid = r_result['control_id'] if r_result else 'FAIL'
        b_match = "v" if b_cid == expected else "x"
        r_match = "v" if r_cid == expected else "x"

        results.append((i, sentence[:50], expected, b_cid, b_match, r_cid, r_match))
        print(f"\n  >> Baseline: {b_cid} [{b_match}] | RAG: {r_cid} [{r_match}] | Expected: {expected}")

    # Summary table
    print(f"\n{'=' * 80}")
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'No':>3} | {'Expected':>8} | {'Baseline':>10} | {'Match':>5} | {'RAG':>10} | {'Match':>5}")
    print(f"{'-'*3}-+-{'-'*8}-+-{'-'*10}-+-{'-'*5}-+-{'-'*10}-+-{'-'*5}")
    for no, sent, exp, b_cid, b_m, r_cid, r_m in results:
        print(f"{no:>3} | {exp:>8} | {b_cid:>10} | {b_m:>5} | {r_cid:>10} | {r_m:>5}")

    print(f"\n{'=' * 80}")
    print("TEST SELESAI")


if __name__ == "__main__":
    main()
