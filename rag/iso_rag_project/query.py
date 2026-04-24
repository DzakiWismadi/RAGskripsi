"""
Interactive query tool for ISO 27001 control retrieval.
Run: python query.py
"""

import sys
sys.path.insert(0, ".")
from retrieval.retrieve import retrieve_top3, format_retrieved_for_prompt


def main():
    print("=" * 60)
    print("  ISO 27001 Control Retrieval (Top-3)")
    print("  Ketik kalimat audit, lalu tekan Enter.")
    print("  Ketik 'exit' atau tekan Ctrl+C untuk keluar.")
    print("=" * 60)

    while True:
        try:
            query = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSampai jumpa!")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            print("Sampai jumpa!")
            break

        results = retrieve_top3(query)
        print()
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['control_id']}] {r['title']}")
            print(f"     Score: {r['similarity_score']:.4f}")
            print(f"     {r['description'][:120]}...")
            print()


if __name__ == "__main__":
    main()
