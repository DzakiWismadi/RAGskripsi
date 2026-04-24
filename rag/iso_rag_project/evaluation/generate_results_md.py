# evaluation/generate_results_md.py
# Generates results/experiment_results.md from combined_results.csv + progress JSON.
# Can be re-run anytime to update the markdown with latest data.

import csv
import json
import os

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
CSV_PATH = os.path.join(RESULTS_DIR, "combined_results.csv")
PROGRESS_PATH = os.path.join(RESULTS_DIR, "experiment_progress.json")
OUTPUT_PATH = os.path.join(RESULTS_DIR, "experiment_results.md")


def generate():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        prog = json.load(f)

    total_rows = prog["total_rows"]
    completed = len(rows)

    # Count accuracies
    b_ctrl = sum(1 for r in rows if r["baseline_control"] == r["ground_truth_control"])
    r_ctrl = sum(1 for r in rows if r["rag_control"] == r["ground_truth_control"])
    b_appl = sum(1 for r in rows if r["baseline_applicable"] == r["ground_truth_applicable"] and r["baseline_applicable"] != "FAIL")
    r_appl = sum(1 for r in rows if r["rag_applicable"] == r["ground_truth_applicable"] and r["rag_applicable"] != "FAIL")
    b_stat = sum(1 for r in rows if r["baseline_status"] == r["ground_truth_status"] and r["baseline_status"] != "FAIL")
    r_stat = sum(1 for r in rows if r["rag_status"] == r["ground_truth_status"] and r["rag_status"] != "FAIL")
    fails = sum(1 for r in rows if r["baseline_control"] == "FAIL" or r["rag_control"] == "FAIL")

    b_times = [float(r["baseline_time"]) for r in rows if r["baseline_time"]]
    r_times = [float(r["rag_time"]) for r in rows if r["rag_time"]]

    pct = lambda n, d: f"{100*n/d:.1f}%" if d > 0 else "0%"

    lines = []

    # --- Header ---
    lines.append("# Experiment Results")
    lines.append("")
    lines.append(f"> Auto-generated from `combined_results.csv` ({completed}/{total_rows} rows)")
    lines.append("")

    # --- Progress ---
    lines.append("## Progress")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Rows | {total_rows} |")
    lines.append(f"| Completed | {completed}/{total_rows} ({pct(completed, total_rows)}) |")
    lines.append(f"| Total Runs | {len(prog['runs'])} |")
    lines.append(f"| Total Time | {prog['total_elapsed_seconds']/60:.1f} min |")
    lines.append("")

    # --- Accuracy ---
    lines.append("## Accuracy Summary")
    lines.append("")
    lines.append("| Metric | Baseline | RAG | Winner |")
    lines.append("|--------|----------|-----|--------|")

    def winner(b, r):
        if b > r: return "Baseline"
        if r > b: return "RAG"
        return "Tie"

    lines.append(f"| Control Accuracy | {b_ctrl}/{completed} ({pct(b_ctrl, completed)}) | {r_ctrl}/{completed} ({pct(r_ctrl, completed)}) | {winner(b_ctrl, r_ctrl)} |")
    lines.append(f"| Applicability Accuracy | {b_appl}/{completed} ({pct(b_appl, completed)}) | {r_appl}/{completed} ({pct(r_appl, completed)}) | {winner(b_appl, r_appl)} |")
    lines.append(f"| Status Accuracy | {b_stat}/{completed} ({pct(b_stat, completed)}) | {r_stat}/{completed} ({pct(r_stat, completed)}) | {winner(b_stat, r_stat)} |")
    lines.append(f"| Failures | {fails} | — | — |")
    lines.append("")

    # --- Latency ---
    lines.append("## Latency")
    lines.append("")
    lines.append("| Metric | Baseline | RAG |")
    lines.append("|--------|----------|-----|")
    b_avg = sum(b_times) / len(b_times) if b_times else 0
    r_avg = sum(r_times) / len(r_times) if r_times else 0
    lines.append(f"| Avg Response Time | {b_avg:.1f}s | {r_avg:.1f}s |")
    lines.append(f"| Total Time | {sum(b_times):.0f}s | {sum(r_times):.0f}s |")
    lines.append("")

    # --- Detail Table ---
    lines.append("## Detailed Results — Control Prediction")
    lines.append("")
    lines.append("| # | Input (truncated) | Ground Truth | Baseline Pred | B | RAG Pred | R | Retrieved Top-3 | B Time | R Time |")
    lines.append("|---|-------------------|-------------|---------------|---|----------|---|-----------------|--------|--------|")

    for i, r in enumerate(rows, 1):
        sent = r["sentence"][:55].replace("|", "/")
        if len(r["sentence"]) > 55:
            sent += "..."
        gt = r["ground_truth_control"]
        bl = r["baseline_control"]
        rg = r["rag_control"]
        b_m = "Y" if bl == gt else "N"
        r_m = "Y" if rg == gt else "N"
        retr = r["retrieved_controls"].replace(";", ", ")
        lines.append(f"| {i} | {sent} | {gt} | {bl} | {b_m} | {rg} | {r_m} | {retr} | {r['baseline_time']}s | {r['rag_time']}s |")

    lines.append("")

    # --- Applicability & Status Table ---
    lines.append("## Detailed Results — Applicability & Status")
    lines.append("")
    lines.append("| # | Control | GT Appl | B Appl | B | R Appl | R | GT Status | B Status | B | R Status | R |")
    lines.append("|---|---------|---------|--------|---|--------|---|-----------|----------|---|----------|---|")

    for i, r in enumerate(rows, 1):
        gt = r["ground_truth_control"]
        gt_a = r["ground_truth_applicable"]
        b_a = r["baseline_applicable"]
        r_a = r["rag_applicable"]
        gt_s = r["ground_truth_status"]
        b_s = r["baseline_status"]
        r_s = r["rag_status"]
        ba_m = "Y" if b_a == gt_a else "N"
        ra_m = "Y" if r_a == gt_a else "N"
        bs_m = "Y" if b_s == gt_s else "N"
        rs_m = "Y" if r_s == gt_s else "N"
        lines.append(f"| {i} | {gt} | {gt_a} | {b_a} | {ba_m} | {r_a} | {ra_m} | {gt_s} | {b_s} | {bs_m} | {r_s} | {rs_m} |")

    lines.append("")

    # --- Run History ---
    lines.append("## Run History")
    lines.append("")
    lines.append("| Run | Timestamp | Processed | Baseline Correct | RAG Correct | Fails | Time | Stop Reason |")
    lines.append("|-----|-----------|-----------|-----------------|-------------|-------|------|-------------|")
    for run in prog["runs"]:
        lines.append(f"| {run['run']} | {run['timestamp']} | {run['processed']} | {run['baseline_correct']} | {run['rag_correct']} | {run['fails']} | {run['elapsed_seconds']}s | {run['stopped_reason']} |")

    lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {OUTPUT_PATH} ({len(lines)} lines, {completed} data rows)")


if __name__ == "__main__":
    generate()
