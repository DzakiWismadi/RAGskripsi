# evaluation/retrieval_eval.py
# Computes Recall@3, Recall@1, similarity scores, retrieval quality metrics.

import csv
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retrieval.retrieve import retrieve_top3

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit_gold_standard.csv")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def load_gold_standard():
    rows = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def run_retrieval_eval():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    gold = load_gold_standard()
    total = len(gold)

    hit_at_1 = 0
    hit_at_3 = 0
    top1_scores = []
    scores_when_hit = []
    scores_when_miss = []
    details = []

    print(f"=== Retrieval Evaluation ===")
    print(f"Total rows: {total}")
    print()

    start = time.time()

    for i, row in enumerate(gold, 1):
        sentence = row["sentence"]
        gt_control = row["control_id"]

        retrieved = retrieve_top3(sentence)
        top3_ids = [c["control_id"] for c in retrieved]
        top3_scores = [c["similarity_score"] for c in retrieved]

        is_hit_1 = top3_ids[0] == gt_control if top3_ids else False
        is_hit_3 = gt_control in top3_ids

        if is_hit_1:
            hit_at_1 += 1
        if is_hit_3:
            hit_at_3 += 1

        if top3_scores:
            top1_scores.append(top3_scores[0])

        if is_hit_3:
            scores_when_hit.append(top3_scores[0] if top3_scores else 0)
        else:
            scores_when_miss.append(top3_scores[0] if top3_scores else 0)

        details.append({
            "sentence": sentence,
            "gold_control": gt_control,
            "top1_control": top3_ids[0] if top3_ids else "",
            "top2_control": top3_ids[1] if len(top3_ids) > 1 else "",
            "top3_control": top3_ids[2] if len(top3_ids) > 2 else "",
            "top1_score": f"{top3_scores[0]:.4f}" if top3_scores else "",
            "top2_score": f"{top3_scores[1]:.4f}" if len(top3_scores) > 1 else "",
            "top3_score": f"{top3_scores[2]:.4f}" if len(top3_scores) > 2 else "",
            "hit_at_1": "Yes" if is_hit_1 else "No",
            "hit_at_3": "Yes" if is_hit_3 else "No",
        })

        if i % 20 == 0 or i == total:
            print(f"  [{i}/{total}] Recall@1={hit_at_1/i:.3f} Recall@3={hit_at_3/i:.3f}")

    elapsed = time.time() - start

    # --- Compute summary metrics ---
    recall_1 = hit_at_1 / total if total else 0
    recall_3 = hit_at_3 / total if total else 0
    avg_top1 = sum(top1_scores) / len(top1_scores) if top1_scores else 0
    avg_hit = sum(scores_when_hit) / len(scores_when_hit) if scores_when_hit else 0
    avg_miss = sum(scores_when_miss) / len(scores_when_miss) if scores_when_miss else 0

    # --- Save metrics report ---
    lines = []
    lines.append("=" * 50)
    lines.append("RETRIEVAL EVALUATION METRICS")
    lines.append("=" * 50)
    lines.append(f"Total queries:              {total}")
    lines.append(f"Recall@1:                   {recall_1:.4f} ({hit_at_1}/{total})")
    lines.append(f"Recall@3:                   {recall_3:.4f} ({hit_at_3}/{total})")
    lines.append(f"Avg similarity (top-1):     {avg_top1:.4f}")
    lines.append(f"Avg similarity (hit@3):     {avg_hit:.4f}  (n={len(scores_when_hit)})")
    lines.append(f"Avg similarity (miss@3):    {avg_miss:.4f}  (n={len(scores_when_miss)})")
    lines.append(f"Evaluation time:            {elapsed:.1f}s")
    lines.append("")

    report = "\n".join(lines)
    print()
    print(report)

    metrics_path = os.path.join(RESULTS_DIR, "retrieval_metrics.txt")
    with open(metrics_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {metrics_path}")

    # --- Save detail CSV ---
    detail_path = os.path.join(RESULTS_DIR, "retrieval_detail.csv")
    fieldnames = [
        "sentence", "gold_control",
        "top1_control", "top2_control", "top3_control",
        "top1_score", "top2_score", "top3_score",
        "hit_at_1", "hit_at_3",
    ]
    with open(detail_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(details)
    print(f"Saved: {detail_path}")


if __name__ == "__main__":
    run_retrieval_eval()
