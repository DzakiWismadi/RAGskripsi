"""
Speed test: qwen2.5:3b on ISO 27001 audit sentences.
"""
import sys
import os
import time
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval.retrieve import retrieve_top3, format_retrieved_for_prompt

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"
PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm", "prompt_template.txt")

with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    TEMPLATE = f.read().strip()

TESTS = [
    ("Karyawan tidak pernah mendapat pelatihan keamanan informasi.", "A.6.3"),
    ("Backup data tidak pernah diuji pemulihannya.", "A.8.13"),
    ("Jaringan kantor tidak memiliki firewall.", "A.8.20"),
    ("Kata sandi karyawan hanya terdiri dari 4 digit angka tanpa kompleksitas.", "A.5.17"),
    ("Data pribadi pelanggan dikirim melalui email tanpa enkripsi.", "A.5.34"),
]


def call_llm(prompt):
    start = time.time()
    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "temperature": 0.0,
        "stream": False,
        "options": {"num_predict": 256, "num_ctx": 1024},
    }, timeout=300)
    elapsed = time.time() - start
    return resp.json().get("response", ""), elapsed


def extract_json(text):
    import re
    match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def main():
    print("=" * 80)
    print(f"Speed Test: {MODEL} — RAG Pipeline")
    print("=" * 80)

    results = []

    for i, (sentence, expected) in enumerate(TESTS, 1):
        # Retrieve
        retrieved = retrieve_top3(sentence)
        context = format_retrieved_for_prompt(retrieved)
        ret_ids = [r["control_id"] for r in retrieved]

        # Build RAG prompt
        prompt = f"""{TEMPLATE}

Berikut adalah kontrol ISO 27001 yang paling relevan:

{context}

Gunakan HANYA kontrol di atas sebagai referensi.

Kalimat audit:
"{sentence}"

Jawab dalam format JSON:"""

        # Call LLM
        raw, elapsed = call_llm(prompt)
        data = extract_json(raw)
        cid = data.get("control_id", "?") if data else "FAIL"
        match = "v" if cid == expected else "x"

        results.append((i, sentence[:55], expected, cid, match, elapsed, ret_ids))

        print(f"\nTest {i}: {sentence}")
        print(f"  Retrieved : {ret_ids}")
        print(f"  Expected  : {expected}")
        print(f"  Got       : {cid} [{match}]")
        print(f"  Time      : {elapsed:.1f}s")
        if data:
            print(f"  Status    : {data.get('implementation_status', '?')}")
            j = data.get('justification', '')
            print(f"  Justif    : {j[:100]}")

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"{'No':>3} | {'Expected':>8} | {'Got':>8} | {'OK':>2} | {'Time':>7} | Retrieved")
    print(f"{'-'*3}-+-{'-'*8}-+-{'-'*8}-+-{'-'*2}-+-{'-'*7}-+-{'-'*30}")
    total_time = 0
    correct = 0
    for no, sent, exp, cid, m, t, rids in results:
        print(f"{no:>3} | {exp:>8} | {cid:>8} | {m:>2} | {t:>6.1f}s | {rids}")
        total_time += t
        if m == "v":
            correct += 1

    print(f"\nAccuracy: {correct}/{len(results)}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Avg time per query: {total_time/len(results):.1f}s")


if __name__ == "__main__":
    main()
