# Baseline RAG Specification

## 1. Extracted Baseline RAG (From Code)
1. **Document ingestion**: `iso_rag_project` ingests control knowledge from `data\iso_controls.json` (93 Annex A controls). In NovaTrix runtime, retrieval still points to this external project path via `RAG_PROJECT_PATH` and Python bridge (`backend\src\services\ragService.js`).
2. **Chunking strategy**: no token/window chunking pipeline is implemented. Retrieval unit is one full control record (control-level unit), encoded from `title | objective | description`.
3. **Embedding generation**: `embedding\embedding_model.py` loads `paraphrase-multilingual-MiniLM-L12-v2`, encodes controls/query, casts to `float32`, then L2-normalizes vectors.
4. **Vector storage**: `embedding\build_index.py` builds FAISS `IndexFlatIP` and persists to `data\faiss_index.bin`; metadata saved in `data\index_metadata.json`.
5. **Query embedding**: `retrieval\retrieve.py` calls `encode_texts([query])` using the same embedding model and normalization.
6. **Similarity search**: `index.search(query_embedding, k)` on FAISS inner product over normalized vectors (cosine-equivalent); baseline uses top-3 (`retrieve_top3`).
7. **Context assembly**: retrieved controls are formatted (`format_retrieved_for_prompt`) and injected into `llm\prompt_template.txt` by `rag\rag_pipeline.py`.
8. **LLM generation**: `llm\llm_wrapper.py` calls local Ollama (`qwen2.5:3b` default in code), extracts JSON, validates schema, and returns structured output. NovaTrix can also call OpenRouter after the same shared retrieval stage.

## 2. Embedding Pipeline
3) Embedding Pipeline
Model: paraphrase-multilingual-MiniLM-L12-v2
Embedding dim: 384
Local inference via: sentence-transformers (Python, SentenceTransformer)
Index-time representation: title | objective | description per control record
Query-time representation: raw user query sentence
Normalization: L2-normalized vectors (cosine similarity via inner product)

## 3. Vector Storage
4) Vector Storage
Store: FAISS file-based index (`data\faiss_index.bin`) with side metadata (`data\index_metadata.json`)
Index type: IndexFlatIP
Metadata: model_name, embedding_dim, num_controls, ordered control_ids, index_type, normalization

## 4. Architecture Validation (Legacy vs NovaTrix)
- **Differences**: legacy is a direct Python pipeline; NovaTrix is orchestration (Node) with provider routing (`LOCAL`/`API`/`HTTP`) and persistent run logging (`RagTestRun`).
- **Intended vs actual**:
  - `RAG-ARCHITECTURE-AUDIT-LEGACY-vs-NOVATRIX.md` is broadly aligned with current code for LOCAL/API shared retrieval behavior.
  - `RAG-FLOW-COMPARISON.md` states API mode skips retrieval, but current `ragService.js` API path now executes `runSharedRetrieval` before OpenRouter generation. This document is stale versus implementation.
- **Missing components (for backend-native architecture)**: no native Node vector index build/store; retrieval depends on external legacy Python project and FAISS artifacts.
- **Overengineering vs baseline objective**: multi-provider fallback logic, strict post-hoc JSON coercion, and external bridge modes add operational complexity beyond a pure dense baseline.

## 5. Paper 16 Baseline RAG Reconstruction
- Paper scope is **legal provision retrieval**, not end-to-end RAG generation.
- Explicit dense baseline in paper:
  1. Input audit issue text.
  2. Encode query as dense vector with **BAAI-bge-large-zh-v1.5**.
  3. Compare against pre-encoded legal provision vectors using cosine similarity.
  4. Return top-k legal provisions.
- Explicit corpus/index details in paper:
  - Legal provisions are pre-encoded with BAAI-bge-large-zh-v1.5.
  - Embedding size is **1024**.
  - Vector store is **Chroma-based vector store**.
- For baseline RAG components not explicitly defined in Paper 16:
  - Chunking strategy: not mentioned
  - Prompt template for answer generation: not mentioned
  - LLM answer synthesis after retrieval: not mentioned
  - Output schema for generated answer: not mentioned

## 6. Missing Component Recommendations

### Vector DB Comparison
| Component | Option | Pros | Cons | Suitability |
| --- | --- | --- | --- | --- |
| Vector DB | FAISS | Very simple local setup, fast dense retrieval, good for fixed corpus, easy thesis reproducibility | No built-in server/API, fewer operational features (multi-user, RBAC, durability tooling) | **High** for skripsi baseline V1 |
| Vector DB | ChromaDB | Developer-friendly API, metadata filtering, persistent local DB, aligns with Paper 16 mention (Chroma-based) | Heavier than FAISS-only baseline, extra service/runtime complexity if scaled | Medium-High |
| Vector DB | Milvus | Strong scalability and production features, distributed search | Highest setup/ops complexity, overkill for small-medium thesis corpus | Low for baseline |

### Final Recommendation
Use **FAISS** for the clean baseline implementation (V1).  
Reason: it is the lowest-complexity path, already proven in your current codebase, easy to deploy locally for skripsi experiments, and sufficient for dense-only retrieval quality measurement without adding infrastructure overhead. This best matches the required performance-vs-simplicity tradeoff for baseline comparison against advanced variants.

## 7. Final Clean Baseline RAG (READY TO IMPLEMENT)
1. Build knowledge corpus from ISO Annex A controls (single control-level records).
2. Encode all records with one embedding model (same model for index/query).
3. L2-normalize vectors and index with dense FAISS `IndexFlatIP`.
4. At runtime: encode query, retrieve top-k by cosine-equivalent similarity.
5. Inject retrieved controls into a fixed prompt template.
6. Generate one structured answer with LLM.
7. Persist retrieved IDs/scores + final answer for evaluation.

**Constraints for baseline purity**:
- No BM25/hybrid retrieval
- No query rewriting
- No HyDE
- No reranking/RRF
- No multi-stage retrieval
