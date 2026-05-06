#!/usr/bin/env python3
"""Fast evaluation: only test the most promising alpha values."""
import sys
import json
import numpy as np
from pathlib import Path

V3_ROOT = Path(__file__).resolve().parents[1]
V1_ROOT = V3_ROOT.parent / "ragV1"
if str(V1_ROOT) not in sys.path:
    sys.path.insert(0, str(V1_ROOT))
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))

from hybrid.hybrid_retriever import HybridRetriever
from reranking.cross_encoder_reranker import rerank_documents, _normalize

controls_path = V1_ROOT / "data" / "iso_controls_enriched.json"
retriever = HybridRetriever(controls_path=controls_path)

queries_path = V1_ROOT / "evaluation" / "test_queries.json"
queries = json.loads(queries_path.read_text(encoding="utf-8"))
print(f"Loaded {len(queries)} queries")

def compute_hit(pred, gt):
    return 1.0 if any(p in gt for p in pred[:3]) else 0.0

def compute_mrr(pred, gt):
    for i, p in enumerate(pred[:3], 1):
        if p in gt:
            return 1.0 / i
    return 0.0

# ── Pre-compute retrieval for pool=20 ──────────────────────────────────────
print("\nPre-computing hybrid retrieval (pool=20)...")
precomputed = []
for item in queries:
    query = item["query"]
    gt = item.get("ground_truth", [])
    if not gt:
        continue
    ret = retriever.retrieve(query=query, k=20, method_order=["hybrid"])
    docs20 = ret["hybrid_results"]
    baseline_ids = [d["control_id"] for d in docs20[:3]]
    precomputed.append({
        "query": query, "gt": gt, "docs20": docs20, "baseline_ids": baseline_ids,
    })

# Show baseline
base_hits = [compute_hit(p["baseline_ids"], p["gt"]) for p in precomputed]
base_mrrs = [compute_mrr(p["baseline_ids"], p["gt"]) for p in precomputed]
n = len(precomputed)
print(f"Baseline (hybrid top-3, no rerank): Hit@3={sum(base_hits)/n:.3f}  MRR={sum(base_mrrs)/n:.3f}")

# ── Test alphas with pool=20 ───────────────────────────────────────────────
print("\nAlpha sweep (pool=20, top_n=3):")
print(f"{'Alpha':>8} {'Hit@3':>8} {'MRR':>8} {'Queries improved/degraded'}")
print("-" * 60)

for alpha in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    hits, mrrs = [], []
    improved, degraded = 0, 0
    for p in precomputed:
        reranked = rerank_documents(query=p["query"], retrieved_docs=p["docs20"], top_n=3, alpha=alpha)
        rr_ids = [d["control_id"] for d in reranked]
        hit = compute_hit(rr_ids, p["gt"])
        mrr = compute_mrr(rr_ids, p["gt"])
        hits.append(hit)
        mrrs.append(mrr)
        base_mrr = compute_mrr(p["baseline_ids"], p["gt"])
        if mrr > base_mrr:
            improved += 1
        elif mrr < base_mrr:
            degraded += 1
    avg_hit = sum(hits) / n
    avg_mrr = sum(mrrs) / n
    delta = ""
    if improved > 0 or degraded > 0:
        delta = f"  (+{improved}/-{degraded})"
    print(f"{alpha:>8.1f} {avg_hit:>8.3f} {avg_mrr:>8.3f}{delta}")

# ── Per-query detail at best alpha ─────────────────────────────────────────
print("\n" + "=" * 80)
print("Per-query detail at alpha=0.0 (pure hybrid, no cross-encoder):")
for p in precomputed:
    reranked = rerank_documents(query=p["query"], retrieved_docs=p["docs20"], top_n=3, alpha=0.0)
    rr_ids = [d["control_id"] for d in reranked]
    print(f"  Q: {p['query'][:60]}...")
    print(f"    GT={p['gt']}")
    print(f"    Baseline(3): {p['baseline_ids']}")
    print(f"    Reranked(20->3, a=0.0): {rr_ids}")
    print(f"    Hit: {compute_hit(rr_ids, p['gt'])}  MRR: {compute_mrr(rr_ids, p['gt'])}")

print("\nPer-query detail at alpha=0.3:")
for p in precomputed:
    reranked = rerank_documents(query=p["query"], retrieved_docs=p["docs20"], top_n=3, alpha=0.3)
    rr_ids = [d["control_id"] for d in reranked]
    base_mrr = compute_mrr(p["baseline_ids"], p["gt"])
    new_mrr = compute_mrr(rr_ids, p["gt"])
    change = "SAME" if new_mrr == base_mrr else ("UP" if new_mrr > base_mrr else "DOWN")
    print(f"  Q: {p['query'][:60]}...")
    print(f"    GT={p['gt']}")
    print(f"    Baseline(3): {p['baseline_ids']}  MRR={base_mrr:.4f}")
    print(f"    Reranked(20->3, a=0.3): {rr_ids}  MRR={new_mrr:.4f}  [{change}]")

print("\nDone.")
