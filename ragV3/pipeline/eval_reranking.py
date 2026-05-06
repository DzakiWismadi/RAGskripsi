#!/usr/bin/env python3
"""
Fast evaluation: test key alpha values with pre-fetched Top-20 candidates.
Only loads the cross-encoder ONCE and only does hybrid retrieval ONCE per query.
"""
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
from reranking.cross_encoder_reranker import rerank_documents, get_model, _doc_to_rerank_text

# ── Setup ──────────────────────────────────────────────────────────────────
controls_path = V1_ROOT / "data" / "iso_controls_enriched.json"
gt_path = V1_ROOT / "evaluation" / "test_queries.json"

with open(gt_path, "r", encoding="utf-8") as f:
    queries = json.load(f)

retriever = HybridRetriever(controls_path=controls_path)
print(f"Loaded {len(queries)} queries and {len(retriever.controls)} controls")

def compute_mrr(pred_ids, gt_ids, k=3):
    for idx, cid in enumerate(pred_ids[:k], start=1):
        if cid in gt_ids:
            return 1.0 / idx
    return 0.0

def compute_hit(pred_ids, gt_ids, k=3):
    for cid in pred_ids[:k]:
        if cid in gt_ids:
            return 1.0
    return 0.0

def normalize(arr):
    mn, mx = float(np.min(arr)), float(np.max(arr))
    if mx - mn < 1e-12:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


# ── Step 1: Pre-fetch Top-20 for all queries ──────────────────────────────
print("\n" + "=" * 80)
print("STEP 1: Pre-fetching Top-20 candidates for each query")
print("=" * 80)

all_candidates = []  # list of (query_text, gt, top20_docs, top20_ids)
for item in queries:
    query = item["query"]
    gt = item.get("ground_truth", [])
    if not gt:
        continue
    retrieval = retriever.retrieve(query=query, k=20, method_order=["hybrid"])
    docs = retrieval["hybrid_results"]
    ids = [d["control_id"] for d in docs]
    all_candidates.append((query, gt, docs, ids))

    gt_in_top3 = [g for g in gt if g in ids[:3]]
    gt_in_top20 = [g for g in gt if g in ids[:20]]
    gt_missed = [g for g in gt if g not in ids[:20]]
    print(f"  Q: {query[:60]}...")
    print(f"    GT={gt}  Top3={ids[:3]}  GT@3={gt_in_top3}  GT@20={gt_in_top20}  Missed={gt_missed}")

# Baseline
base_hits = [compute_hit(c[3][:3], c[1]) for c in all_candidates]
base_mrrs = [compute_mrr(c[3][:3], c[1]) for c in all_candidates]
n = len(all_candidates)
print(f"\n  BASELINE (Top-3 hybrid):  Hit@3={sum(base_hits)/n:.3f}  MRR={sum(base_mrrs)/n:.3f}")


# ── Step 2: Score all candidates with cross-encoder ONCE ──────────────────
print("\n" + "=" * 80)
print("STEP 2: Cross-encoder scoring")
print("=" * 80)

model = get_model()
print("  Model loaded.")

all_ce_scores = []  # list of np arrays
all_hybrid_scores = []
for query, gt, docs, ids in all_candidates:
    pairs = [(query, _doc_to_rerank_text(doc)) for doc in docs]
    ce_scores = np.array(model.predict(pairs, show_progress_bar=False), dtype=np.float32)
    hybrid_scores = np.array([float(doc.get("hybrid_score", 0.0)) for doc in docs], dtype=np.float32)
    all_ce_scores.append(ce_scores)
    all_hybrid_scores.append(hybrid_scores)

print("  Cross-encoder scoring done.")


# ── Step 3: Grid search over alpha values ─────────────────────────────────
print("\n" + "=" * 80)
print("STEP 3: Alpha sweep (using pre-computed scores)")
print("=" * 80)

alphas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

print(f"\n{'Alpha':>6s}  {'Hit@3':>6s}  {'MRR':>6s}  {'Recall@3':>9s}  {'Prec@3':>7s}")
print("-" * 45)

best_mrr = 0
best_alpha = 0

for alpha in alphas:
    hits, mrrs, recalls, precs = [], [], [], []
    for i, (query, gt, docs, ids) in enumerate(all_candidates):
        ce_norm = normalize(all_ce_scores[i])
        hyb_norm = normalize(all_hybrid_scores[i])
        combined = alpha * ce_norm + (1 - alpha) * hyb_norm

        # Sort by combined score
        ranked_indices = np.argsort(-combined)[:3]
        ranked_ids = [docs[j]["control_id"] for j in ranked_indices]

        h = compute_hit(ranked_ids, gt)
        m = compute_mrr(ranked_ids, gt)
        inter = len(set(ranked_ids) & set(gt))
        hits.append(h)
        mrrs.append(m)
        recalls.append(inter / max(len(gt), 1))
        precs.append(inter / 3)

    avg_hit = sum(hits) / n
    avg_mrr = sum(mrrs) / n
    avg_recall = sum(recalls) / n
    avg_prec = sum(precs) / n
    marker = ""
    if avg_mrr > best_mrr:
        best_mrr = avg_mrr
        best_alpha = alpha
        marker = " <-- BEST"
    elif alpha == 0.0:
        marker = " (pure hybrid)"
    elif alpha == 1.0:
        marker = " (pure CE)"

    print(f"  {alpha:4.1f}  {avg_hit:6.3f}  {avg_mrr:6.3f}  {avg_recall:9.3f}  {avg_prec:7.3f}{marker}")

print(f"\n  BEST ALPHA = {best_alpha} with MRR = {best_mrr:.3f}")


# ── Step 4: Per-query breakdown at best alpha ─────────────────────────────
print("\n" + "=" * 80)
print(f"STEP 4: Per-query breakdown at alpha={best_alpha}")
print("=" * 80)

for i, (query, gt, docs, ids) in enumerate(all_candidates):
    ce_norm = normalize(all_ce_scores[i])
    hyb_norm = normalize(all_hybrid_scores[i])
    combined = best_alpha * ce_norm + (1 - best_alpha) * hyb_norm

    ranked_indices = np.argsort(-combined)[:3]
    ranked_ids = [docs[j]["control_id"] for j in ranked_indices]

    hybrid_top3 = ids[:3]
    m_before = compute_mrr(hybrid_top3, gt)
    m_after = compute_mrr(ranked_ids, gt)

    print(f"  Q: {query[:60]}...")
    print(f"    GT:           {gt}")
    print(f"    Hybrid Top-3: {hybrid_top3}  (MRR={m_before:.4f})")
    print(f"    Reranked Top-3: {ranked_ids}  (MRR={m_after:.4f})")
    if m_after > m_before:
        print(f"    -> IMPROVED (+{m_after - m_before:.4f})")
    elif m_after < m_before:
        print(f"    -> DEGRADED ({m_after - m_before:.4f})")
    else:
        print(f"    -> SAME")


# ── Step 5: Also try pool=10 vs pool=20 ───────────────────────────────────
print("\n" + "=" * 80)
print("STEP 5: Pool size comparison at best alpha")
print("=" * 80)

for pool_size in [5, 10, 15, 20]:
    hits, mrrs = [], []
    for i, (query, gt, docs, ids) in enumerate(all_candidates):
        pool = docs[:pool_size]
        ce_norm = normalize(all_ce_scores[i][:pool_size])
        hyb_norm = normalize(all_hybrid_scores[i][:pool_size])
        combined = best_alpha * ce_norm + (1 - best_alpha) * hyb_norm
        ranked_indices = np.argsort(-combined)[:3]
        ranked_ids = [pool[j]["control_id"] for j in ranked_indices]
        hits.append(compute_hit(ranked_ids, gt))
        mrrs.append(compute_mrr(ranked_ids, gt))
    print(f"  Pool={pool_size:2d}:  Hit@3={sum(hits)/n:.3f}  MRR={sum(mrrs)/n:.3f}")


print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
