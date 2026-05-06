# Baseline RAG V1 (Hybrid)

## 1. Pipeline Analysis

### Data Source
- Static JSON file: `data\iso_controls.json`
- Retrieval unit: 1 control record
- Fields used in retrieval text representation: `title`, `objective`, `description`
- Additional fields used in output: `control_id`, `title`, `objective`, `description`

### Retrieval Flow
1. User query enters NovaTrix (`/api/ragtest` or `/api/ai/chat` when provider is RAG).
2. Backend (`ragService.js`) calls Python retrieval (`retrieve_top3`) from `iso_rag_project`.
3. Python retrieval encodes query with SentenceTransformer and searches FAISS index.
4. Top-3 controls are formatted into prompt context.
5. Prompt goes to LLM (local Ollama in LOCAL mode, OpenRouter in API mode).
6. Output is parsed/normalized and returned.

### Dense Retrieval
- Model: `paraphrase-multilingual-MiniLM-L12-v2`
- Embedding dim: `384`
- Document representation: `title | objective | description`
- Query representation: raw user query text
- Similarity: cosine-equivalent via L2-normalized vectors + FAISS `IndexFlatIP`

### Sparse Retrieval (if exists)
- In `iso_rag_project` and current NovaTrix retrieval path: **not implemented**
- No BM25 / TF-IDF / inverted index retrieval stage in active runtime path

### Hybrid Strategy
- Current runtime pipeline: **not hybrid**
- Dense-only retrieval is used before generation
- No dense+sparse fusion score method in active code path

### LLM Generation
- Local mode: Ollama `/api/generate`, model in code default `qwen2.5:3b`
- API mode: OpenRouter call after shared retrieval prompt construction
- Prompt flow: base template + retrieved controls + user query + JSON-output constraint

### Observations
- Actual retrieval is dense-only despite provider complexity in backend.
- Backend adds multi-provider routing and output coercion, but not hybrid retrieval.
- `RAG-FLOW-COMPARISON.md` states API has no retrieval; current `ragService.js` now performs shared retrieval in API path before generation.

## 2. Hybrid Baseline Definition (V1)

### Retrieval Components
- Dense: SentenceTransformer embedding + cosine similarity search over all controls
- Sparse: BM25 lexical retrieval over the same control text (`title | objective | description`)

### Fusion Strategy
- Method: **weighted sum**
- Formula:
  - `dense_norm = minmax(dense_score)`
  - `sparse_norm = minmax(bm25_score)`
  - `hybrid_score = 0.6 * dense_norm + 0.4 * sparse_norm`
- Fixed parameters:
  - Dense weight = `0.6`
  - Sparse weight = `0.4`

### Top-k Strategy
- `k = 3` (default)
- Dense top-k: highest dense score
- Sparse top-k: highest BM25 score
- Hybrid top-k: highest fused score

### Final Pipeline
1. Load static JSON controls.
2. Build control text per record (`title | objective | description`).
3. Encode all controls with one embedding model (dense index in memory).
4. Build BM25 statistics on same control texts.
5. For each query:
   - compute dense cosine scores
   - compute BM25 scores
   - normalize both score vectors
   - compute weighted-sum hybrid score (single-stage)
6. Take hybrid top-k controls.
7. Build prompt from hybrid top-k context.
8. Generate final answer with LLM.

### Constraints
- No query expansion
- No reranking
- Single-stage hybrid retrieval

## 3. Required Adjustments

### Remove
- Multi-provider orchestration for baseline experiment logic
- External HTTP bridge and model fallback complexity
- Non-essential output coercion not tied to retrieval baseline validity

### Add (if missing)
- BM25 sparse retriever
- Explicit dense+sparse fusion logic
- Transparent score reporting (`dense_score`, `sparse_score`, `hybrid_score`)

### Fix
- Keep retrieval source and text representation identical across dense and sparse paths
- Fuse over same candidate universe (all controls), then take one final top-k
- Use fixed fusion parameters for reproducibility

## 4. Dense Component
Model: `paraphrase-multilingual-MiniLM-L12-v2`  
Dim: dynamic from model (expected 384)  
Similarity: cosine (dot product on normalized vectors)

## 5. Sparse Component
BM25 implemented in pure Python:
- tokenization (lowercase alphanumeric terms)
- per-term document frequency and IDF
- Okapi BM25 scoring with fixed `k1=1.5`, `b=0.75`

## 6. Fusion Strategy
Weighted sum with fixed weights:
- `hybrid_score = 0.6 * dense_norm + 0.4 * sparse_norm`
- `dense_norm` and `sparse_norm` use min-max normalization

## 7. Top-k Retrieval
- Default `k=3`
- System returns:
  - `dense_results`
  - `sparse_results`
  - `hybrid_results`
- Final generation uses `hybrid_results`

## 8. LLM Generation
- Wrapper: `llm\llm_wrapper.py`
- Endpoint: Ollama `http://localhost:11434/api/generate`
- Model default: `qwen2.5:3b`
- Prompt source: `prompts\prompt_template.txt`
- Output: parsed JSON when possible, otherwise raw text

## 9. Limitations
- no query expansion
- no reranking
- no multi-stage retrieval
- sparse tokenizer is simple (no stemming/lemmatization)
- assumes local Ollama availability for final answer generation

cd D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1
python app\app.py

http://127.0.0.1:5001/