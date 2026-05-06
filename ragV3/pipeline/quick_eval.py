#!/usr/bin/env python3
"""Quick evaluation: test a few alpha values with pool=20 only."""
import sys, json, numpy as np
from pathlib import Path

V3_ROOT = Path(__file__).resolve().parents[1]
V1_ROOT = V3_ROOT.parent / "ragV1"
for p in [str(V1_ROOT), str(V3_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from hybrid.hybrid_retriever import HybridRetriever
from reranking.cross_encoder_reranker import get_model, _doc_to_rerank_text, _normalize

controls_path = V1_ROOT / "data" / "iso_controls_enriched.json"
gt_path = V1_ROOT / "evaluation" / "test_queries.json"

with open(gt_path, "r", encoding="utf-8") as f:
    queries = json.load(f)

retriever = HybridRetriever(controls_path=controls_path)
print(f"Loaded {len(queries)} queries, {len(retriever.controls)} controls")

def compute_mrr(pred, gt, k=3):
    for i, cid in enumerate(pred[:k], 1):
        if cid in gt:
            return 1.0 / i
    return 0.0

def compute_hit(pred, gt, k=3):
    return 1.0 if any(cid in gt for cid in pred[:k]) else 0.0

# Step 1: Pre-fetch Top-20 for all queries
print("\n" + "="*80)
print("Pre-fetching Top-20 candidates...")
print("="*80)
all_candidates = []
for item in queries:
    q = item["query"]
    gt = item.get("ground_truth", [])
    if not gt:
        continue
    ret = retriever.retrieve(query=q, k=20, method_order=["hybrid"])
    docs = ret["hybrid_results"]
    all_candidates.append({"query": q, "gt": gt, "docs": docs})
    h3 = [d["control_id"] for d in docs[:3]]
    print(f"  GT={gt}  Hybrid@3={h3}  hit={compute_hit(h3,gt):.0f}  mrr={compute_mrr(h3,gt):.3f}")

# Step 2: Score with cross-encoder once
print("\n" + "="*80)
print("Cross-encoder scoring...")
print("="*80)
model = get_model()
print("Model loaded.")

for entry in all_candidates:
    pairs = [(entry["query"], _doc_to_rerank_text(d)) for d in entry["docs"]]
    ce_raw = np.array(model.predict(pairs, show_progress_bar=False), dtype=np.float32)
    hyb_raw = np.array([float(d.get("hybrid_score", 0.0)) for d in entry["docs"]], dtype=np.float32)
    entry["ce_raw"] = ce_raw
    entry["hyb_raw"] = hyb_raw
    # Print CE ranking vs hybrid ranking for top-20
    ce_order = np.argsort(-ce_raw)
    print(f"\n  Q: {entry['query'][:50]}... GT={entry['gt']}")
    print(f"    Hybrid@3: {[entry['docs'][i]['control_id'] for i in range(min(3,len(entry['docs'])))]}")
    print(f"    CE@3:     {[entry['docs'][i]['control_id'] for i in ce_order[:3]]}")
    print(f"    CE scores top5: {[(entry['docs'][ce_order[i]]['control_id'], f'{ce_raw[ce_order[i]]:.3f}') for i in range(min(5,len(ce_order)))]}")

# Step 3: Grid search alpha with pool=20
print("\n" + "="*80)
print("ALPHA GRID SEARCH (pool=20)")
print("="*80)
print(f"{'Alpha':>6} {'Hit@3':>8} {'MRR':>8} {'Recall@3':>10} {'Prec@3':>10}")
print("-" * 50)

for alpha in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    hits, mrrs, recalls, precs = [], [], [], []
    for entry in all_candidates:
        ce_n = _normalize(entry["ce_raw"])
        hyb_n = _normalize(entry["hyb_raw"])
        combined = alpha * ce_n + (1 - alpha) * hyb_n
        order = np.argsort(-combined)
        reranked_ids = [entry["docs"][i]["control_id"] for i in order[:3]]
        gt = entry["gt"]
        hits.append(compute_hit(reranked_ids, gt))
        mrrs.append(compute_mrr(reranked_ids, gt))
        inter = len(set(reranked_ids) & set(gt))
        recalls.append(inter / max(len(gt), 1))
        precs.append(inter / 3)
    n = len(all_candidates)
    print(f"{alpha:6.1f} {sum(hits)/n:8.3f} {sum(mrrs)/n:8.3f} {sum(recalls)/n:10.3f} {sum(precs)/n:10.3f}")

# Step 4: Also test pool=10 with best alphas
print("\n" + "="*80)
print("POOL SIZE COMPARISON (best alphas)")
print("="*80)
for pool in [5, 10, 15, 20]:
    for alpha in [0.0, 0.3, 0.5, 0.7]:
        hits, mrrs = [], []
        for entry in all_candidates:
            docs = entry["docs"][:pool]
            ce_raw = entry["ce_raw"][:pool]
            hyb_raw = entry["hyb_raw"][:pool]
            ce_n = _normalize(ce_raw)
            hyb_n = _normalize(hyb_raw)
            combined = alpha * ce_n + (1 - alpha) * hyb_n
            order = np.argsort(-combined)
            reranked_ids = [docs[i]["control_id"] for i in order[:3]]
            gt = entry["gt"]
            hits.append(compute_hit(reranked_ids, gt))
            mrrs.append(compute_mrr(reranked_ids, gt))
        n = len(all_candidates)
        print(f"  pool={pool:2d} α={alpha:.1f}  Hit@3={sum(hits)/n:.3f}  MRR={sum(mrrs)/n:.3f}")

print("\nDone.")
