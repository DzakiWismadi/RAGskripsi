#!/usr/bin/env python3
"""
Compare cross-encoder models: old (ms-marco-MiniLM) vs new (stsb-distilroberta).
Pre-fetches candidates once, then sweeps alpha for both models.
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
from sentence_transformers import CrossEncoder
from reranking.cross_encoder_reranker import _doc_to_rerank_text

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

all_candidates = []
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
    print(f"  Q: {query[:50]}...")
    print(f"    GT={gt}  Top3={ids[:3]}  GT@3={gt_in_top3}  GT@20={gt_in_top20}")

n = len(all_candidates)
base_hits = [compute_hit(c[3][:3], c[1]) for c in all_candidates]
base_mrrs = [compute_mrr(c[3][:3], c[1]) for c in all_candidates]
print(f"\n  BASELINE (Top-3 hybrid):  Hit@3={sum(base_hits)/n:.3f}  MRR={sum(base_mrrs)/n:.3f}")


# ── Step 2: Score with both models ─────────────────────────────────────────
MODELS = [
    ("ms-marco-MiniLM-L-6-v2 (OLD)", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
    ("stsb-distilroberta-base (NEW)", "cross-encoder/stsb-distilroberta-base"),
]

all_model_scores = {}  # model_name -> list of (ce_scores, hybrid_scores)

for model_label, model_name in MODELS:
    print(f"\n{'=' * 80}")
    print(f"STEP 2: Scoring with {model_label}")
    print("=" * 80)

    model = CrossEncoder(model_name)
    ce_data = []
    for query, gt, docs, ids in all_candidates:
        pairs = [(query, _doc_to_rerank_text(doc)) for doc in docs]
        ce_scores = np.array(model.predict(pairs, show_progress_bar=False), dtype=np.float32)
        hybrid_scores = np.array(
            [float(doc.get("hybrid_score", 0.0)) for doc in docs], dtype=np.float32
        )
        ce_data.append((ce_scores, hybrid_scores))

        # Show score distribution for first query
        if len(ce_data) == 1:
            print(f"  Sample scores for Q: {query[:40]}...")
            for j in range(min(5, len(docs))):
                print(
                    f"    {docs[j]['control_id']:8s}  CE={ce_scores[j]:8.4f}  "
                    f"Hyb={hybrid_scores[j]:.4f}  {docs[j]['title'][:50]}"
                )

    all_model_scores[model_label] = ce_data
    del model


# ── Step 3: Alpha sweep for each model ─────────────────────────────────────
alphas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

for model_label, _ in MODELS:
    ce_data = all_model_scores[model_label]
    print(f"\n{'=' * 80}")
    print(f"STEP 3: Alpha sweep for {model_label}")
    print("=" * 80)

    print(f"\n  {'Alpha':>6s}  {'Hit@3':>6s}  {'MRR':>6s}  {'Recall@3':>9s}  {'Prec@3':>7s}")
    print("  " + "-" * 45)

    best_mrr = 0
    best_alpha = 0

    for alpha in alphas:
        hits, mrrs, recalls, precs = [], [], [], []
        for i, (query, gt, docs, ids) in enumerate(all_candidates):
            ce_scores, hyb_scores = ce_data[i]
            ce_norm = normalize(ce_scores)
            hyb_norm = normalize(hyb_scores)
            combined = alpha * ce_norm + (1 - alpha) * hyb_norm

            ranked_indices = np.argsort(-combined)[:3]
            ranked_ids = [docs[j]["control_id"] for j in ranked_indices]

            hits.append(compute_hit(ranked_ids, gt))
            mrrs.append(compute_mrr(ranked_ids, gt))
            inter = len(set(ranked_ids) & set(gt))
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

        print(
            f"  {alpha:4.1f}  {avg_hit:6.3f}  {avg_mrr:6.3f}  "
            f"{avg_recall:9.3f}  {avg_prec:7.3f}{marker}"
        )

    print(f"\n  BEST ALPHA = {best_alpha} with MRR = {best_mrr:.3f}")

    # Per-query breakdown at best alpha
    print(f"\n  Per-query at alpha={best_alpha}:")
    for i, (query, gt, docs, ids) in enumerate(all_candidates):
        ce_scores, hyb_scores = ce_data[i]
        ce_norm = normalize(ce_scores)
        hyb_norm = normalize(hyb_scores)
        combined = best_alpha * ce_norm + (1 - best_alpha) * hyb_norm

        ranked_indices = np.argsort(-combined)[:3]
        ranked_ids = [docs[j]["control_id"] for j in ranked_indices]

        hybrid_top3 = ids[:3]
        m_before = compute_mrr(hybrid_top3, gt)
        m_after = compute_mrr(ranked_ids, gt)

        direction = "SAME"
        if m_after > m_before:
            direction = f"IMPROVED (+{m_after - m_before:.4f})"
        elif m_after < m_before:
            direction = f"DEGRADED ({m_after - m_before:.4f})"

        print(
            f"    GT={gt}  Hyb={hybrid_top3}  RR={ranked_ids}  "
            f"MRR {m_before:.2f}->{m_after:.2f}  {direction}"
        )


# ── Step 4: Pool size comparison ────────────────────────────────────────────
print(f"\n{'=' * 80}")
print("STEP 4: Pool size comparison at best alpha per model")
print("=" * 80)

for model_label, _ in MODELS:
    ce_data = all_model_scores[model_label]
    print(f"\n  {model_label}:")
    for pool_size in [5, 10, 15, 20]:
        hits, mrrs = [], []
        for i, (query, gt, docs, ids) in enumerate(all_candidates):
            pool = docs[:pool_size]
            ce_norm = normalize(ce_data[i][0][:pool_size])
            hyb_norm = normalize(ce_data[i][1][:pool_size])
            combined = 0.3 * ce_norm + 0.7 * hyb_norm  # moderate alpha
            ranked_indices = np.argsort(-combined)[:3]
            ranked_ids = [pool[j]["control_id"] for j in ranked_indices]
            hits.append(compute_hit(ranked_ids, gt))
            mrrs.append(compute_mrr(ranked_ids, gt))
        print(f"    Pool={pool_size:2d} (alpha=0.3):  Hit@3={sum(hits)/n:.3f}  MRR={sum(mrrs)/n:.3f}")


print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
