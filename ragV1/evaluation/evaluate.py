import argparse
import json
import sys
from pathlib import Path
from typing import Any


def evaluate_dataset(project_root: Path, k: int = 3) -> dict[str, Any]:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from hybrid.hybrid_retriever import HybridRetriever

    data_path = project_root / "evaluation" / "test_queries.json"
    with data_path.open("r", encoding="utf-8") as f:
        dataset = json.load(f)

    retriever = HybridRetriever(project_root / "data" / "iso_controls.json")
    results: list[dict[str, Any]] = []

    hit_total = 0.0
    recall_total = 0.0

    for item in dataset:
        query = item["query"]
        gt = list(item["ground_truth"])
        retrieval = retriever.retrieve(query=query, k=k)
        predicted = [r["control_id"] for r in retrieval["hybrid_results"]]
        overlap = len(set(predicted) & set(gt))
        hit = 1 if overlap > 0 else 0
        recall = overlap / max(len(gt), 1)
        hit_total += hit
        recall_total += recall
        results.append(
            {
                "query": query,
                "predicted": predicted,
                "ground_truth": gt,
                "hit": hit,
                "recall": recall,
            }
        )

    n = max(len(results), 1)
    return {
        "k": k,
        "results": results,
        "average_hit": hit_total / n,
        "average_recall": recall_total / n,
    }


def _print_report(report: dict[str, Any]) -> None:
    k = report["k"]
    for i, row in enumerate(report["results"], start=1):
        print(f"Query {i}:")
        print(f"Top-{k}: [{', '.join(row['predicted'])}]")
        print(f"GT: [{', '.join(row['ground_truth'])}]")
        print(f"Hit@{k}: {row['hit']}")
        print(f"Recall@{k}: {row['recall']:.3f}")
        print()

    print(f"Average Hit@{k}: {report['average_hit']:.3f}")
    print(f"Average Recall@{k}: {report['average_recall']:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ragV1 hybrid retrieval on test_queries.json")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    report = evaluate_dataset(project_root=root, k=args.k)
    _print_report(report)
