# Feasible User Testing Phases

## Phase 1: Data Preparation (Manual)
- Human prepares `iso_controls.json` (Annex A.5-A.8) and `audit_gold_standard.csv` (100+ labeled sentences)
- Test: validate JSON structure and CSV format with a simple script

## Phase 2: Embedding & Index Build
- Human runs `build_index.py` to embed ISO controls with all-MiniLM-L6-v2 and build FAISS index
- Test: terminal query — input a sample audit sentence, verify top-3 retrieved controls make sense

## Phase 3: Baseline (Prompt-Only) Sanity Check
- Human inputs a single audit sentence via terminal to `prompt_only.py`
- Test: check that CybersecurityRiskAnalyst (8B Q4_0) returns valid JSON with correct schema (`control_id`, `applicable`, `implementation_status`, etc.)

## Phase 4: RAG Pipeline Sanity Check
- Human inputs same sentence via terminal to `rag_pipeline.py`
- Test: compare RAG output vs baseline output — verify retrieved context is injected and response differs meaningfully

## Phase 5: Full Experiment Run
- Human runs `experiment_runner.py` on the entire gold standard dataset (no manual input needed)
- Output: `combined_results.csv` with baseline vs RAG predictions for all 100+ sentences

## Phase 6: Metrics & Retrieval Evaluation
- Human runs `metrics.py` and `retrieval_eval.py`
- Output: accuracy, precision, recall, F1, confusion matrices, Recall@3, latency report

## Phase 7: Robustness Testing
- Human runs `robustness_test.py` with paraphrased/noisy variants
- Output: prediction stability %, variance rate, consistency metrics

## Phase 8: Error Analysis & Thesis Writing
- Human reviews misclassified cases, compares failure patterns between baseline vs RAG
- Output: discussion-ready insights for Chapter 4/5 of thesis
