# evaluation/metrics.py
# Computes accuracy, precision, recall, F1, confusion matrices, and latency report.

import csv
import os
from collections import defaultdict

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
INPUT_PATH = os.path.join(RESULTS_DIR, "combined_results.csv")


def load_results():
    """Load combined_results.csv, return list of row dicts."""
    rows = []
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def filter_valid(rows):
    """Exclude rows where baseline or RAG returned FAIL."""
    return [r for r in rows if r["baseline_control"] != "FAIL" and r["rag_control"] != "FAIL"]


def accuracy(rows, gt_key, pred_key):
    """Simple exact-match accuracy."""
    if not rows:
        return 0.0
    correct = sum(1 for r in rows if r[gt_key] == r[pred_key])
    return correct / len(rows)


def precision_recall_f1_macro(rows, gt_key, pred_key):
    """Compute macro-averaged precision, recall, F1 for multi-class classification."""
    # Collect all classes
    classes = sorted(set(r[gt_key] for r in rows) | set(r[pred_key] for r in rows))

    total_p, total_r, total_f1 = 0.0, 0.0, 0.0
    class_count = 0

    for cls in classes:
        tp = sum(1 for r in rows if r[gt_key] == cls and r[pred_key] == cls)
        fp = sum(1 for r in rows if r[gt_key] != cls and r[pred_key] == cls)
        fn = sum(1 for r in rows if r[gt_key] == cls and r[pred_key] != cls)

        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

        total_p += p
        total_r += r
        total_f1 += f1
        class_count += 1

    if class_count == 0:
        return 0.0, 0.0, 0.0
    return total_p / class_count, total_r / class_count, total_f1 / class_count


def build_confusion_matrix(rows, gt_key, pred_key):
    """Build confusion matrix as dict-of-dicts. Returns (labels, matrix)."""
    labels = sorted(set(r[gt_key] for r in rows) | set(r[pred_key] for r in rows))
    matrix = defaultdict(lambda: defaultdict(int))
    for r in rows:
        matrix[r[gt_key]][r[pred_key]] += 1
    return labels, matrix


def save_confusion_csv(labels, matrix, path):
    """Save confusion matrix as CSV pivot table."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["actual \\ predicted"] + labels)
        for gt in labels:
            row = [gt] + [matrix[gt][pred] for pred in labels]
            writer.writerow(row)


def compute_latency(rows):
    """Compute latency stats from all rows (including FAIL rows)."""
    b_times = []
    r_times = []
    for r in rows:
        try:
            b_times.append(float(r["baseline_time"]))
        except (ValueError, KeyError):
            pass
        try:
            r_times.append(float(r["rag_time"]))
        except (ValueError, KeyError):
            pass

    return {
        "baseline_avg": sum(b_times) / len(b_times) if b_times else 0,
        "rag_avg": sum(r_times) / len(r_times) if r_times else 0,
        "baseline_total": sum(b_times),
        "rag_total": sum(r_times),
        "total": sum(b_times) + sum(r_times),
        "n_baseline": len(b_times),
        "n_rag": len(r_times),
    }


def run_metrics():
    all_rows = load_results()
    valid = filter_valid(all_rows)

    print(f"Total rows: {len(all_rows)}, Valid (non-FAIL): {len(valid)}")
    print()

    # --- Accuracy ---
    metrics = {}
    for method in ["baseline", "rag"]:
        ctrl_acc = accuracy(valid, "ground_truth_control", f"{method}_control")
        appl_acc = accuracy(valid, "ground_truth_applicable", f"{method}_applicable")
        stat_acc = accuracy(valid, "ground_truth_status", f"{method}_status")
        p, r, f1 = precision_recall_f1_macro(valid, "ground_truth_control", f"{method}_control")

        metrics[method] = {
            "control_accuracy": ctrl_acc,
            "applicable_accuracy": appl_acc,
            "status_accuracy": stat_acc,
            "precision": p,
            "recall": r,
            "f1": f1,
        }

    # --- Print and save evaluation metrics ---
    lines = []
    lines.append("=" * 60)
    lines.append("EVALUATION METRICS")
    lines.append("=" * 60)
    lines.append(f"Total rows: {len(all_rows)}, Valid (non-FAIL): {len(valid)}")
    lines.append("")

    header = f"{'Metric':<30} {'Baseline':>12} {'RAG':>12} {'Delta':>12}"
    lines.append(header)
    lines.append("-" * 66)

    for label, key in [
        ("Control Accuracy", "control_accuracy"),
        ("Applicability Accuracy", "applicable_accuracy"),
        ("Status Accuracy", "status_accuracy"),
        ("Precision (macro)", "precision"),
        ("Recall (macro)", "recall"),
        ("F1 Score (macro)", "f1"),
    ]:
        b = metrics["baseline"][key]
        r = metrics["rag"][key]
        d = r - b
        sign = "+" if d >= 0 else ""
        lines.append(f"{label:<30} {b:>11.4f} {r:>12.4f} {sign}{d:>11.4f}")

    lines.append("")
    report = "\n".join(lines)
    print(report)

    eval_path = os.path.join(RESULTS_DIR, "evaluation_metrics.txt")
    with open(eval_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {eval_path}")

    # --- Confusion matrices ---
    for method in ["baseline", "rag"]:
        labels, matrix = build_confusion_matrix(valid, "ground_truth_control", f"{method}_control")
        path = os.path.join(RESULTS_DIR, f"confusion_matrix_{method}.csv")
        save_confusion_csv(labels, matrix, path)
        print(f"Saved: {path}")

    # --- Latency report ---
    lat = compute_latency(all_rows)
    lat_lines = []
    lat_lines.append("=" * 50)
    lat_lines.append("LATENCY REPORT")
    lat_lines.append("=" * 50)
    lat_lines.append(f"Baseline avg response time:  {lat['baseline_avg']:.2f}s  (n={lat['n_baseline']})")
    lat_lines.append(f"RAG avg response time:       {lat['rag_avg']:.2f}s  (n={lat['n_rag']})")
    lat_lines.append(f"Baseline total time:         {lat['baseline_total']:.1f}s ({lat['baseline_total']/60:.1f}m)")
    lat_lines.append(f"RAG total time:              {lat['rag_total']:.1f}s ({lat['rag_total']/60:.1f}m)")
    lat_lines.append(f"Combined total time:         {lat['total']:.1f}s ({lat['total']/60:.1f}m)")
    lat_lines.append("")
    lat_report = "\n".join(lat_lines)
    print()
    print(lat_report)

    lat_path = os.path.join(RESULTS_DIR, "latency_report.txt")
    with open(lat_path, "w", encoding="utf-8") as f:
        f.write(lat_report)
    print(f"Saved: {lat_path}")


if __name__ == "__main__":
    run_metrics()
