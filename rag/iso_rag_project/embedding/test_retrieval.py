# embedding/test_retrieval.py
# Smoke test for retrieval pipeline with 5 test sentences covering A.5-A.8

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from retrieval.retrieve import retrieve_top3, format_retrieved_for_prompt

# Test sentences covering all 4 annex categories
TEST_CASES = [
    {
        "query": "Organisasi harus memiliki kebijakan keamanan informasi yang disetujui manajemen puncak.",
        "expected_controls": ["A.5.1", "A.5.2"],
        "category": "A.5 (Kebijakan)",
    },
    {
        "query": "Semua karyawan baru harus menjalani pemeriksaan latar belakang sebelum diberikan akses ke sistem.",
        "expected_controls": ["A.6.1", "A.6.2"],
        "category": "A.6 (SDM)",
    },
    {
        "query": "Akses fisik ke ruang server harus dibatasi menggunakan kartu akses dan biometrik.",
        "expected_controls": ["A.7.2", "A.7.1", "A.7.3"],
        "category": "A.7 (Fisik)",
    },
    {
        "query": "Sistem harus dilindungi dari malware dengan antivirus yang diperbarui secara otomatis.",
        "expected_controls": ["A.8.7", "A.8.8"],
        "category": "A.8 (Teknologi)",
    },
    {
        "query": "Backup data harus dilakukan secara rutin dan diuji pemulihannya setiap kuartal.",
        "expected_controls": ["A.8.13", "A.8.14"],
        "category": "A.8 (Backup)",
    },
]


def run_tests():
    print("=" * 70)
    print("Retrieval Smoke Test")
    print("=" * 70)

    total = 0
    hits = 0

    for i, tc in enumerate(TEST_CASES, 1):
        print(f"\n--- Test {i}: {tc['category']} ---")
        print(f"Query: {tc['query']}")
        print(f"Expected: {tc['expected_controls']}")

        results = retrieve_top3(tc["query"])

        print(f"Top-3 results:")
        retrieved_ids = []
        for j, r in enumerate(results, 1):
            print(f"  {j}. {r['control_id']} - {r['title']} (score: {r['similarity_score']:.4f})")
            retrieved_ids.append(r["control_id"])

        # Soft check: at least one expected control in top-3
        hit = any(eid in retrieved_ids for eid in tc["expected_controls"])
        total += 1
        if hit:
            hits += 1
            print(f"  -> HIT (expected control found in top-3)")
        else:
            print(f"  -> MISS (no expected control in top-3)")

    print(f"\n{'=' * 70}")
    print(f"Results: {hits}/{total} test cases have at least one expected control in top-3")

    if hits == total:
        print("ALL TESTS PASSED")
    else:
        print(f"WARNING: {total - hits} test(s) did not match expected controls")

    # Show formatted output example
    print(f"\n{'=' * 70}")
    print("Example formatted output for LLM prompt:")
    print("=" * 70)
    example_results = retrieve_top3(TEST_CASES[0]["query"])
    print(format_retrieved_for_prompt(example_results))


if __name__ == "__main__":
    run_tests()
