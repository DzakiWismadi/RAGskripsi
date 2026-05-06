"""
Comprehensive reranking evaluation script.
Tests multiple configurations to find the optimal pipeline setup.

Compares:
  1. Old pipeline: Top-3 retrieval → rerank Top-3 (alpha=1.0 pure CE)
  2. New pipeline: Top-20 retrieval → rerank Top-20 → final Top-3
     - With varying alpha values
     - With enriched vs basic doc text
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────
V3_ROOT = Path(__file__).resolve().parent
V1_ROOT = V3_ROOT.parent / "ragV1"
sys.path.insert(0, str(V1_ROOT))
sys.path.insert(0, str(V3_ROOT))

from hybrid.hybrid_retriever import HybridRetriever
from reranking.cross_encoder_reranker import rerank_documents, get_model, _doc_to_rerank_text

# ── Load data ──────────────────────────────────────────────────────────────
controls_path = V1_ROOT / "data" / "iso_controls_enriched.json"
test_queries_path = V1_ROOT / "evaluation" / "test_queries.json"

with open(controls_path, "r", encoding="utf-8") as f:
    controls = json.load(f)

with open(test_queries_path, "r", encoding="utf-8") as f:
    test_queries = json.load(f)

# Build enriched control lookup
control_map = {c["control_id"]: c for c in controls}

# Initialize retriever
print("Initializing HybridRetriever with enriched controls...")
retriever = HybridRetriever(controls_path=controls_path)

# Pre-load cross-encoder model
print("Pre-loading cross-encoder model...")
model = get_model()
print("Model loaded.\n")


# ── Metric computation ────────────────────────────────────────────────────
def compute_metrics(predicted_ids, ground_truth, k=3):
    gt = [str(x).strip() for x in ground_truth if str(x).strip()]
    pred = [str(x).strip() for x in predicted_ids[:k] if str(x).strip()]
    if not gt:
        return {"hit": None, "recall": None, "precision": None, "mrr": None}
    inter = 0
    seen = set()
    for cid in pred:
        if cid in gt and cid not in seen:
            inter += 1
            seen.add(cid)
    hit = 1.0 if inter > 0 else 0.0
    recall = inter / max(len(gt), 1)
    precision = inter / max(k, 1)
    first_rank = 0
    for idx, cid in enumerate(pred, start=1):
        if cid in gt:
            first_rank = idx
            break
    mrr = 1.0 / first_rank if first_rank > 0 else 0.0
    return {"hit": hit, "recall": recall, "precision": precision, "mrr": mrr}


def avg_metrics(metrics_list):
    """Average a list of metric dicts, skipping None values."""
    keys = ["hit", "recall", "precision", "mrr"]
    result = {}
    for key in keys:
        vals = [m[key] for m in metrics_list if m[key] is not None]
        result[key] = sum(vals) / len(vals) if vals else 0.0
    return result


# ── Candidate pool analysis ───────────────────────────────────────────────
print("=" * 80)
print("SECTION 1: CANDIDATE POOL ANALYSIS")
print("=" * 80)

gt_in_top3 = 0
gt_in_top10 = 0
gt_in_top20 = 0
gt_in_top_all = 0
total_gt_items = 0
gt_missed_in_top3_but_in_top20 = 0

for tq in test_queries:
    query = tq["query"]
    gt = tq.get("ground_truth", [])
    total_gt_items += len(gt)
    
    result = retriever.retrieve(query=query, k=20, method_order=["hybrid"])
    hybrid_ids = [r["control_id"] for r in result["hybrid_results"]]
    
    hits_t3 = set(gt) & set(hybrid_ids[:3])
    hits_t10 = set(gt) & set(hybrid_ids[:10])
    hits_t20 = set(gt) & set(hybrid_ids[:20])
    hits_all = set(gt) & set(hybrid_ids)
    
    gt_in_top3 += len(hits_t3)
    gt_in_top10 += len(hits_t10)
    gt_in_top20 += len(hits_t20)
    gt_in_top_all += len(hits_all)
    
    missed_t3 = set(gt) - set(hybrid_ids[:3])
    found_t20 = missed_t3 & set(hybrid_ids[3:20])
    gt_missed_in_top3_but_in_top20 += len(found_t20)
    
    for g in gt:
        if g in hybrid_ids:
            rank = hybrid_ids.index(g) + 1
            marker = "✓" if rank <= 3 else ("○" if rank <= 20 else "✗")
            print(f"  {marker} {g} at rank {rank:2d} in hybrid | Query: {query[:60]}...")
        else:
            print(f"  ✗ {g} NOT FOUND in top-20 | Query: {query[:60]}...")

print(f"\n--- Pool Coverage Summary ---")
print(f"  Total GT items:             {total_gt_items}")
print(f"  GT found in Top-3:          {gt_in_top3}/{total_gt_items} ({gt_in_top3/total_gt_items*100:.1f}%)")
print(f"  GT found in Top-10:         {gt_in_top10}/{total_gt_items} ({gt_in_top10/total_gt_items*100:.1f}%)")
print(f"  GT found in Top-20:         {gt_in_top20}/{total_gt_items} ({gt_in_top20/total_gt_items*100:.1f}%)")
print(f"  GT found in all 93:         {gt_in_top_all}/{total_gt_items} ({gt_in_top_all/total_gt_items*100:.1f}%)")
print(f"  GT missed in T3 but in T20: {gt_missed_in_top3_but_in_top20}/{total_gt_items}")


# ── Pipeline comparison ───────────────────────────────────────────────────
print("\n" + "=" * 80)
print("SECTION 2: PIPELINE CONFIGURATION COMPARISON")
print("=" * 80)

configs = [
    {"name": "Old (r3→rr3, α=1.0)",  "pool_k": 3,  "alpha": 1.0},
    {"name": "Old (r3→rr3, α=0.7)",  "pool_k": 3,  "alpha": 0.7},
    {"name": "New (r20→rr3, α=1.0)", "pool_k": 20, "alpha": 1.0},
    {"name": "New (r20→rr3, α=0.7)", "pool_k": 20, "alpha": 0.7},
    {"name": "New (r20→rr3, α=0.5)", "pool_k": 20, "alpha": 0.5},
    {"name": "New (r20→rr3, α=0.3)", "pool_k": 20, "alpha": 0.3},
    {"name": "New (r20→rr3, α=0.0)", "pool_k": 20, "alpha": 0.0},  # pure hybrid baseline
]

all_results = {}
per_query_results = {}

for cfg in configs:
    name = cfg["name"]
    pool_k = cfg["pool_k"]
    alpha = cfg["alpha"]
    
    metrics_list = []
    q_details = []
    
    for tq in test_queries:
        query = tq["query"]
        gt = tq.get("ground_truth", [])
        
        # Stage 1: Retrieve
        retrieval = retriever.retrieve(query=query, k=pool_k, method_order=["hybrid"])
        retrieved = retrieval["hybrid_results"]
        
        # Stage 2: Rerank
        reranked = rerank_documents(
            query=query, retrieved_docs=retrieved, top_n=3, alpha=alpha
        )
        reranked_ids = [r["control_id"] for r in reranked]
        
        m = compute_metrics(reranked_ids, gt, k=3)
        metrics_list.append(m)
        
        # Get hybrid top-3 for comparison
        hybrid_t3_ids = [r["control_id"] for r in retrieved[:3]]
        hybrid_m = compute_metrics(hybrid_t3_ids, gt, k=3)
        
        q_details.append({
            "query": query[:60],
            "gt": gt,
            "hybrid_t3": hybrid_t3_ids,
            "reranked_t3": reranked_ids,
            "hybrid_mrr": hybrid_m["mrr"],
            "reranked_mrr": m["mrr"],
            "changed": hybrid_t3_ids != reranked_ids,
        })
    
    avg = avg_metrics(metrics_list)
    all_results[name] = avg
    per_query_results[name] = q_details
    
    print(f"\n  Config: {name}")
    print(f"    Hit@3={avg['hit']:.3f}  Recall@3={avg['recall']:.3f}  "
          f"Precision@3={avg['precision']:.3f}  MRR={avg['mrr']:.3f}")


# ── Summary table ──────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("SECTION 3: SUMMARY TABLE")
print("=" * 80)
print(f"{'Config':<30} {'Hit@3':>8} {'Recall@3':>9} {'Prec@3':>8} {'MRR':>8}")
print("-" * 65)
for name, avg in all_results.items():
    print(f"{name:<30} {avg['hit']:>8.3f} {avg['recall']:>9.3f} {avg['precision']:>8.3f} {avg['mrr']:>8.3f}")


# ── Per-query detail ──────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("SECTION 4: PER-QUERY DETAIL (Best New Config vs Old vs Hybrid-only)")
print("=" * 80)

# Find best new config
best_new_name = max(
    [(n, a) for n, a in all_results.items() if "New" in n],
    key=lambda x: (x[1]["mrr"], x[1]["hit"])
)[0]

configs_to_show = [
    "New (r20→rr3, α=0.0)",  # pure hybrid with pool=20
    best_new_name,
    "Old (r3→rr3, α=1.0)",
]

for cfg_name in configs_to_show:
    if cfg_name not in per_query_results:
        continue
    print(f"\n  Config: {cfg_name}")
    print(f"  {'Query':<62} {'GT':<18} {'Top-3':<22} {'MRR':>6}")
    print(f"  {'-'*62} {'-'*18} {'-'*22} {'-'*6}")
    for qd in per_query_results[cfg_name]:
        gt_str = str(qd['gt'])[:16]
        rr_str = str(qd['reranked_t3'])[:20]
        print(f"  {qd['query']:<62} {gt_str:<18} {rr_str:<22} {qd['reranked_mrr']:>6.4f}")


# ── Failure analysis ──────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("SECTION 5: FAILURE ANALYSIS")
print("=" * 80)

# Cases where reranker degrades vs hybrid
print("\n--- Cases where reranker DEGRADES vs pure hybrid (new best config) ---")
degraded = 0
improved = 0
for i, tq in enumerate(test_queries):
    hybrid_r20 = per_query_results.get("New (r20→rr3, α=0.0)", [])
    best_r20 = per_query_results.get(best_new_name, [])
    if i >= len(hybrid_r20) or i >= len(best_r20):
        continue
    
    h_mrr = hybrid_r20[i]["reranked_mrr"]
    b_mrr = best_r20[i]["reranked_mrr"]
    
    if b_mrr < h_mrr:
        degraded += 1
        print(f"  DEGRADED: {tq['query'][:60]}...")
        print(f"    GT: {tq['ground_truth']}")
        print(f"    Hybrid T3: {hybrid_r20[i]['reranked_t3']} (MRR={h_mrr:.4f})")
        print(f"    Reranked:  {best_r20[i]['reranked_t3']} (MRR={b_mrr:.4f})")
    elif b_mrr > h_mrr:
        improved += 1

print(f"\n  Total: {degraded} degraded, {improved} improved, "
      f"{len(test_queries) - degraded - improved} unchanged")


# ── Cross-encoder score analysis ──────────────────────────────────────────
print("\n" + "=" * 80)
print("SECTION 6: CROSS-ENCODER SCORE DISTRIBUTION")
print("=" * 80)

for tq in test_queries[:3]:  # Just first 3 for brevity
    query = tq["query"]
    gt = tq.get("ground_truth", [])
    
    retrieval = retriever.retrieve(query=query, k=20, method_order=["hybrid"])
    retrieved = retrieval["hybrid_results"]
    
    # Get CE scores
    pairs = [(query, _doc_to_rerank_text(doc)) for doc in retrieved]
    ce_scores = model.predict(pairs, show_progress_bar=False)
    
    print(f"\n  Query: {query[:60]}...")
    print(f"  GT: {gt}")
    print(f"  {'Rank':>4} {'Ctrl ID':>8} {'Hybrid':>8} {'CE Score':>9} {'GT?':>5}")
    print(f"  {'-'*4} {'-'*8} {'-'*8} {'-'*9} {'-'*5}")
    for j, (doc, ce_s) in enumerate(zip(retrieved[:10], ce_scores[:10])):
        is_gt = "YES" if doc["control_id"] in gt else ""
        print(f"  {j+1:>4} {doc['control_id']:>8} {doc['hybrid_score']:>8.4f} {float(ce_s):>9.4f} {is_gt:>5}")


print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
