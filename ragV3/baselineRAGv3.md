# Baseline RAG V3 (Hybrid Retrieval + Cross-Encoder Reranking)

## 1. Difference Between V1 and V3

### V1
- Hybrid retrieval only (BM25 + Dense embedding retrieval)
- Final ranked results come directly from fusion score

### V3
- Reuses the same V1 hybrid retrieval pipeline (same chunking, embedding model, indexing data, and BM25 logic)
- Adds a second stage: **Cross-Encoder reranking** on top-k hybrid candidates
- Final ranked results are produced by reranker score, not only fusion score

---

## 2. Cross-Encoder Analysis

## A. What is a Cross Encoder?

A cross encoder is a transformer-based relevance model that receives **query and document together** as one input sequence and outputs a relevance score for that pair.

- **Concept**: direct pairwise relevance estimation
- **Architecture**: one encoder stack jointly attends over query and document tokens
- **Difference vs bi-encoder**:
  - **Bi-encoder / embedding retrieval**: encodes query and document separately, then compares vectors (fast, indexable)
  - **Cross-encoder**: computes token-level interactions across both texts in one forward pass (slower, usually more accurate ranking)

---

## B. How Cross-Encoder Computation Works

For each candidate document, input is formed as:

`[CLS] Query [SEP] Document [SEP]`

Computation flow:
1. Tokenize query-document pair as one sequence.
2. Transformer self-attention lets each query token attend to document tokens (and vice versa).
3. Final representation (commonly around `[CLS]`) is passed to a regression/classification head.
4. Model outputs a **relevance score** (or probability) for that exact pair.
5. Candidates are sorted by this score.

Why slower but more accurate:
- **More accurate**: captures fine-grained token interactions and phrase-level alignment.
- **Slower**: must run one forward pass per (query, document) pair; cannot precompute document embeddings for ANN search like dense retrieval.

---

## C. What Cross-Encoder Needs

- **Model requirement**: pretrained reranker (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`)
- **Input format**: query-document paired text
- **Candidate requirement**: a retrieved candidate set first (from hybrid retrieval)
- **Hardware implication**:
  - GPU improves latency significantly for batch pair scoring
  - CPU is feasible but slower when candidate count grows
- **Why only top-k**:
  - Pairwise scoring cost scales with number of candidates
  - Running cross-encoder on full corpus is computationally expensive
  - Practical design: retrieve top-k fast, rerank only those candidates

---

## D. Relationship with Hybrid Retrieval

Pipeline:

User Query  
→ Hybrid Retrieval (BM25 + Dense, reused from V1)  
→ Top-K Candidates  
→ Cross Encoder Reranking  
→ Final Ranked Results

Hybrid retrieval maximizes recall; cross-encoder improves precision at ranking stage.

---

## 3. Literature Review Mapping (Required Papers)

## Paper 1  
**Enhancing Compliance Checking with Fine-Tuned LLMs and RAG (2025)**

Findings used in V3 design:
- Uses dense retrieval (DPR) as first-pass retrieval, then cross-encoder reranking.
- Emphasizes cross-encoder for finer relevance discrimination and false-positive reduction.
- Notes cross-encoder inference is heavier and should be used after candidate retrieval, not as full-corpus retriever.

Implication for V3:
- Keep fast first-stage retrieval (V1 hybrid), then rerank top-k with cross-encoder.

## Paper 2  
**Novel Hybrid Retrieval and Reranking with Score Fusion for Financial QA**

Findings used in V3 design:
- Dense retrieval + cross-encoder reranking + score fusion gives better retrieval quality than dense-only.
- Defines reranking as pair scoring: \( p_i = g_{rerank}(Q, C_i) \).
- Reports improvements in ranking metrics (MAP/NDCG/Recall/Precision) after reranking stage.

Implication for V3:
- Retain V1 hybrid retrieval and append dedicated reranking stage for ranking quality gains.

## Paper 3  
**Enhancing Retrieval and Re-ranking in RAG: Tax Law Case Study**

Findings used in V3 design:
- Hybrid retrieval (BM25 + dense) improves recall over single retriever.
- Cross-encoder reranking on top candidates improves ranking quality (reported NDCG gain, e.g., 0.39 → 0.44 with bge-reranker-base in study setup).
- Shows layered architecture is effective in regulation-heavy domains.

Implication for V3:
- Architecture should be explicitly layered and traceable:
  **Retrieval → Candidate Docs → Reranking → Final Docs**.

---

## 4. Reranking Pipeline (V3)

1. **Retrieval stage (reused from V1)**  
   `HybridRetriever.retrieve(query, k, method_order=["hybrid"])`
2. **Candidate selection**  
   Use hybrid top-k results as reranker input.
3. **Reranking stage**  
   `rerank_documents(query, retrieved_docs)` with cross-encoder.
4. **Final ranking output**  
   Sort by `rerank_score` descending.

---

## 5. Computational Cost

- Reranking is slower because it performs transformer inference per query-document pair.
- Complexity increases approximately linearly with candidate count (top-k size).
- Despite added latency, reranking improves semantic precision by explicitly modeling cross-token relevance between query and document.

---

## 6. Integration with Existing Pipeline

## Reused from V1
- `hybrid.hybrid_retriever.HybridRetriever`
- `dense/` embedding model path and behavior
- `sparse/` BM25 path and behavior
- Existing control corpus/index source (`data/iso_controls.json`)
- Existing LLM wrapper (`llm.llm_wrapper.generate_answer`)

## Added in V3
- `reranking/cross_encoder_reranker.py`
  - `rerank_documents(query, retrieved_docs)`
- `pipeline/rag_pipeline_v3.py`
  - V3 orchestration: hybrid retrieval (V1) + cross-encoder reranking + timing separation
- App integration in `ragV1/app/app.py`
  - `POST /v3`
  - `GET /history/v3`
  - `GET /history/v3/<slug>`
  - `DELETE /history/v3`

---

## 7. Timing Instrumentation (V3)

V3 records separate timing values:

```python
retrieval_time = ...
reranking_time = ...
total_time = retrieval_time + reranking_time
```

This supports thesis-level latency analysis for retrieval stage vs reranking stage.

