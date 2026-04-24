# evaluation/experiment_runner.py
# Runs baseline and RAG on full gold standard dataset with resume support.
# Time-limited chunks (~10 min default). Re-run to continue where you left off.

import csv
import json
import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from baseline.prompt_only import run_prompt_only_raw
from rag.rag_pipeline import run_rag_raw

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit_gold_standard.csv")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
OUTPUT_PATH = os.path.join(RESULTS_DIR, "combined_results.csv")
PROGRESS_PATH = os.path.join(RESULTS_DIR, "experiment_progress.json")
LOG_PATH = os.path.join(RESULTS_DIR, "experiment_log.txt")

TIME_LIMIT_SECONDS = 10 * 60  # 10 minutes per chunk

FIELDNAMES = [
    "sentence", "ground_truth_control", "baseline_control", "rag_control",
    "ground_truth_applicable", "baseline_applicable", "rag_applicable",
    "ground_truth_status", "baseline_status", "rag_status",
    "baseline_time", "rag_time", "baseline_raw", "rag_raw",
    "retrieved_controls", "retrieval_scores",
]


def load_gold_standard():
    """Load gold standard CSV and return list of row dicts."""
    rows = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_completed_sentences():
    """Load sentences already processed (for resume support)."""
    if not os.path.exists(OUTPUT_PATH):
        return set()
    done = set()
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            done.add(row["sentence"])
    return done


def load_progress():
    """Load cumulative progress tracker."""
    if not os.path.exists(PROGRESS_PATH):
        return {
            "runs": [],
            "total_rows": 0,
            "completed": 0,
            "baseline_correct": 0,
            "rag_correct": 0,
            "fail_count": 0,
            "total_elapsed_seconds": 0.0,
        }
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress):
    """Save cumulative progress tracker."""
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def extract_fields(parsed, prefix):
    """Extract control_id, applicable, implementation_status from parsed dict.
    If parsed is None, returns FAIL for all fields."""
    if parsed is None:
        return {
            f"{prefix}_control": "FAIL",
            f"{prefix}_applicable": "FAIL",
            f"{prefix}_status": "FAIL",
        }
    return {
        f"{prefix}_control": parsed.get("control_id", "FAIL"),
        f"{prefix}_applicable": parsed.get("applicable", "FAIL"),
        f"{prefix}_status": parsed.get("implementation_status", "FAIL"),
    }


def run_experiment():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    gold = load_gold_standard()
    done = load_completed_sentences()
    progress = load_progress()
    total = len(gold)
    remaining = total - len(done)

    if remaining == 0:
        print("=== All rows already processed! ===")
        print(f"Total: {total}, see results/combined_results.csv")
        print(f"Progress log: results/experiment_progress.json")
        return

    # Open log file (append mode — accumulates across all runs)
    log_file = open(LOG_PATH, "a", encoding="utf-8")

    def log(msg=""):
        """Print to console AND write to log file."""
        print(msg)
        log_file.write(msg + "\n")
        log_file.flush()

    # Open in append mode if resuming, write mode if fresh
    is_fresh = len(done) == 0
    mode = "w" if is_fresh else "a"
    f = open(OUTPUT_PATH, mode, newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if is_fresh:
        writer.writeheader()

    chunk_start = time.time()
    fail_count = 0
    baseline_correct = 0
    rag_correct = 0
    processed = 0
    stopped_reason = "all_done"

    run_number = len(progress["runs"]) + 1
    log(f"=== Experiment Runner - Run #{run_number} ===")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Total rows: {total}, Already completed: {len(done)}, Remaining: {remaining}")
    log(f"Time limit: {TIME_LIMIT_SECONDS}s ({TIME_LIMIT_SECONDS/60:.0f} min)")
    log()

    try:
        for i, row in enumerate(gold, 1):
            sentence = row["sentence"]
            gt_control = row["control_id"]
            gt_applicable = row["applicable"]
            gt_status = row["implementation_status"]

            if sentence in done:
                continue

            # Check time limit BEFORE starting a new row
            elapsed = time.time() - chunk_start
            if elapsed >= TIME_LIMIT_SECONDS:
                stopped_reason = "time_limit"
                break

            # --- Baseline ---
            try:
                b_parsed, b_raw, b_time = run_prompt_only_raw(sentence)
            except Exception as e:
                log(f"  [BASELINE ERROR] {e}")
                b_parsed, b_raw, b_time = None, f"ERROR: {e}", 0.0

            # --- RAG ---
            try:
                r_parsed, r_raw, r_time, retrieved = run_rag_raw(sentence)
            except Exception as e:
                log(f"  [RAG ERROR] {e}")
                r_parsed, r_raw, r_time, retrieved = None, f"ERROR: {e}", 0.0, []

            # Extract fields
            b_fields = extract_fields(b_parsed, "baseline")
            r_fields = extract_fields(r_parsed, "rag")

            # Format retrieved controls
            ctrl_ids = ";".join(c["control_id"] for c in retrieved) if retrieved else ""
            ctrl_scores = ";".join(f"{c['similarity_score']:.4f}" for c in retrieved) if retrieved else ""

            # Track accuracy
            b_ok = b_fields["baseline_control"] == gt_control
            r_ok = r_fields["rag_control"] == gt_control
            if b_ok:
                baseline_correct += 1
            if r_ok:
                rag_correct += 1
            if b_fields["baseline_control"] == "FAIL" or r_fields["rag_control"] == "FAIL":
                fail_count += 1

            processed += 1

            # Progress log — show full input + AI responses
            row_num = len(done) + processed
            b_match = "CORRECT" if b_ok else "WRONG"
            r_match = "CORRECT" if r_ok else "WRONG"

            log(f"{'='*70}")
            log(f"[{row_num}/{total}] Ground Truth: {gt_control} | {gt_applicable} | {gt_status}")
            log(f"  INPUT: {sentence}")
            log(f"  --- Baseline ({b_time:.1f}s) [{b_match}] ---")
            log(f"  Control: {b_fields['baseline_control']}  Applicable: {b_fields['baseline_applicable']}  Status: {b_fields['baseline_status']}")
            log(f"  Raw: {b_raw}")
            log(f"  --- RAG ({r_time:.1f}s) [{r_match}] ---")
            log(f"  Control: {r_fields['rag_control']}  Applicable: {r_fields['rag_applicable']}  Status: {r_fields['rag_status']}")
            log(f"  Retrieved: {ctrl_ids}")
            log(f"  Raw: {r_raw}")

            # Write row
            out_row = {
                "sentence": sentence,
                "ground_truth_control": gt_control,
                "ground_truth_applicable": gt_applicable,
                "ground_truth_status": gt_status,
                "baseline_time": f"{b_time:.2f}",
                "rag_time": f"{r_time:.2f}",
                "baseline_raw": b_raw,
                "rag_raw": r_raw,
                "retrieved_controls": ctrl_ids,
                "retrieval_scores": ctrl_scores,
            }
            out_row.update(b_fields)
            out_row.update(r_fields)
            writer.writerow(out_row)
            f.flush()  # Flush after each row for resume safety

    except KeyboardInterrupt:
        stopped_reason = "interrupted"
        log(f"\n--- Interrupted! Progress saved. Re-run to resume. ---")
    finally:
        f.close()

    chunk_elapsed = time.time() - chunk_start
    total_done_now = len(done) + processed
    total_remaining = total - total_done_now

    # Update cumulative progress
    run_entry = {
        "run": run_number,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "processed": processed,
        "baseline_correct": baseline_correct,
        "rag_correct": rag_correct,
        "fails": fail_count,
        "elapsed_seconds": round(chunk_elapsed, 1),
        "stopped_reason": stopped_reason,
    }
    progress["runs"].append(run_entry)
    progress["total_rows"] = total
    progress["completed"] = total_done_now
    progress["baseline_correct"] += baseline_correct
    progress["rag_correct"] += rag_correct
    progress["fail_count"] += fail_count
    progress["total_elapsed_seconds"] += chunk_elapsed
    save_progress(progress)

    # --- Chunk summary ---
    log()
    log(f"=== Run #{run_number} Summary ===")
    log(f"Processed this run:    {processed} rows")
    log(f"Baseline correct:      {baseline_correct}/{processed} ({100*baseline_correct/max(processed,1):.1f}%)")
    log(f"RAG correct:           {rag_correct}/{processed} ({100*rag_correct/max(processed,1):.1f}%)")
    log(f"Failures this run:     {fail_count}")
    log(f"Time this run:         {chunk_elapsed:.1f}s ({chunk_elapsed/60:.1f}m)")
    log(f"Stopped because:       {stopped_reason}")
    log()
    log(f"=== Overall Progress ===")
    log(f"Completed:             {total_done_now}/{total} ({100*total_done_now/total:.1f}%)")
    log(f"Remaining:             {total_remaining}")
    log(f"Total time so far:     {progress['total_elapsed_seconds']:.1f}s ({progress['total_elapsed_seconds']/60:.1f}m)")
    log(f"Cumulative baseline:   {progress['baseline_correct']}/{progress['completed']}")
    log(f"Cumulative RAG:        {progress['rag_correct']}/{progress['completed']}")
    log(f"Cumulative fails:      {progress['fail_count']}")
    if total_remaining > 0 and processed > 0:
        avg_per_row = chunk_elapsed / processed
        est_remaining = avg_per_row * total_remaining
        est_runs = -(-total_remaining // max(processed, 1))  # ceiling div
        log(f"Avg time/row:          {avg_per_row:.1f}s")
        log(f"Est. remaining time:   {est_remaining:.0f}s ({est_remaining/60:.1f}m)")
        log(f"Est. remaining runs:   ~{est_runs}")
    log()
    log(f"Progress saved to: results/experiment_progress.json")
    log(f"Full log saved to: results/experiment_log.txt")
    if total_remaining > 0:
        log(f">>> Re-run this script to continue processing. <<<")
    else:
        log(f">>> All {total} rows processed! Run metrics.py next. <<<")

    log_file.close()


if __name__ == "__main__":
    run_experiment()
