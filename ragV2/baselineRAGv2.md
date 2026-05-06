# Baseline RAG V2 (Query Expansion)

## Overview

 cd "D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2" && start start_server_background.bat

RAG V2 extends the baseline RAG V1 with **Query Expansion** using LLM. This version adds a query reformulation step before retrieval to improve the semantic match between user queries and ISO 27001:2022 controls.

---

## 1. Architecture Comparison: V1 vs V2

### V1 Flow
```
User Query → Hybrid Retrieval (BM25 + Dense) → Result
```

### V2 Flow
```
User Query 
   → Query Expansion (LLM)
   → Expanded Query
   → Hybrid Retrieval (reuse V1)
   → Result
```

### Key Differences

| Aspect | V1 | V2 |
|--------|-----|-----|
| **Pipeline Stage** | Direct retrieval | Query expansion → Retrieval |
| **Query Transformation** | None (raw query) | LLM-based expansion |
| **LLM Usage** | Only for answer generation | Two-stage: expansion + generation |
| **Latency** | Single retrieval time | Expansion time + retrieval time |
| **Query Used for Retrieval** | Original user query | Expanded/rewritten query |
| **Complexity** | Simple | Modular with expansion module |

---

## 2. Query Expansion Module

### 2.1 File Location
- **Module**: `query_expansion/query_expansion.py`
- **Prompt Template**: `prompts/expand_prompt_template.txt`

### 2.2 Implementation Details

#### Function Signature
```python
def query_expansion(query: str) -> dict[str, Any]
```

#### Input
- `query`: Original user query string (audit finding or question)

#### Output
```python
{
    "original_query": str,    # Original input query
    "expanded_query": str,   # LLM-expanded query
    "llm_time": float,      # Time taken for expansion in seconds
}
```

---

## 3. Query Expansion Flow

### 3.1 Step-by-Step Process

#### Step 1: Build Expansion Prompt
```python
def build_expansion_prompt(query: str) -> str:
    template = _load_expand_prompt_template()
    return template.replace("{query}", query)
```

**Prompt Template** (`prompts/expand_prompt_template.txt`):
```
Kamu adalah asisten ahli ISO 27001:2022.
Tugasmu adalah memperluas query audit berikut untuk meningkatkan kualitas pencarian (retrieval) pada knowledge base kontrol ISO 27001:2022 Annex A.

Aturan:
- Tambahkan sinonim istilah teknis yang relevan dengan keamanan informasi
- Sertakan konsep terkait dari standar ISO 27001:2022 Annex A
- Pertahankan maksud asli query
- Jangan mengubah struktur query secara fundamental
- Keluarkan HANYA query yang telah diperluas, tanpa penjelasan atau format tambahan

Query asli: "{query}"

Expanded query:
```

**Prompt Design Principles**:
- Clear role definition (ISO 27001:2022 expert assistant)
- Explicit constraints to maintain original intent
- Instructions for semantic enhancement (synonyms, related concepts)
- Strict output format (only the expanded query)

#### Step 2: Call LLM for Expansion
```python
def call_ollama_expand(prompt: str) -> str:
    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "temperature": 0.0,
        "stream": False,
        "options": {"num_predict": 256},
    }
    resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    return resp.json()["response"].strip()
```

**LLM Configuration**:
- **Model**: `qwen2.5:3b`
- **Temperature**: `0.0` (deterministic)
- **Max Tokens**: `256`
- **Timeout**: 120 seconds
- **Endpoint**: Ollama `http://localhost:11434/api/generate`

#### Step 3: Handle Timing and Errors
```python
def query_expansion(query: str) -> dict[str, Any]:
    prompt = build_expansion_prompt(query)
    
    start = time.perf_counter()
    try:
        raw = call_ollama_expand(prompt)
        llm_time = time.perf_counter() - start
        expanded = raw if raw else query  # Fallback to original if empty
    except requests.RequestException:
        llm_time = time.perf_counter() - start
        expanded = query  # Fallback to original on error
    
    return {
        "original_query": query,
        "expanded_query": expanded,
        "llm_time": llm_time,
    }
```

**Error Handling**:
- If LLM returns empty response → Use original query
- If LLM request fails → Use original query
- Timing is always measured and returned

---

## 4. Pipeline Integration with V1

### 4.1 Reusing V1 Components

**V2 imports from V1**:
```python
from hybrid.hybrid_retriever import HybridRetriever
from llm.llm_wrapper import generate_answer
```

**No Duplication Principle**:
- V2 does NOT reimplement HybridRetriever
- V2 does NOT reimplement BM25 sparse retrieval
- V2 does NOT reimplement dense embedding
- V2 does NOT reimplement LLM generation (except for query expansion)

### 4.2 Full V2 Pipeline

**File**: `pipeline/rag_pipeline_v2.py`

#### Step 1: Query Expansion
```python
def run(self, query: str, k: int = 3) -> dict[str, Any]:
    # Step 1: Expand query using LLM
    expansion = query_expansion(query)
    expanded_query = expansion["expanded_query"]
    llm_time = expansion["llm_time"]
```

#### Step 2: Hybrid Retrieval (V1)
```python
    # Step 2: Use V1's HybridRetriever with expanded query
    retrieval = self.retriever.retrieve(query=expanded_query, k=k)
    retrieval_time = retrieval["timings"]["total_time"]
```

#### Step 3: Build Prompt with Original Query
```python
    # Step 3: Build prompt using ORIGINAL query (not expanded)
    # This preserves user intent in final context
    prompt = self.build_prompt(query=query, hybrid_results=retrieval["hybrid_results"])
```

#### Step 4: Generate Answer
```python
    # Step 4: Generate final answer
    llm_result = generate_answer(prompt)
    answer = llm_result["parsed_json"] or llm_result["raw_text"]
```

#### Step 5: Return Complete Result
```python
    return {
        "original_query": query,
        "expanded_query": expanded_query,  # For inspection
        "dense_results": retrieval["dense_results"],
        "sparse_results": retrieval["sparse_results"],
        "hybrid_results": retrieval["hybrid_results"],
        "answer": answer,
        "timings": {
            "llm_time": llm_time,              # Query expansion time
            "retrieval_time": retrieval_time,    # Hybrid retrieval time
            "total_time": llm_time + retrieval_time,  # Total pipeline time
        },
        "method_order": retrieval["method_order"],
        "fusion": retrieval["fusion"],
    }
```

### 4.3 Timing Breakdown

V2 provides **separate timing metrics**:

| Metric | Description | Source |
|--------|-------------|--------|
| `llm_time` | Time for query expansion | `query_expansion()` |
| `retrieval_time` | Time for hybrid retrieval | `HybridRetriever.retrieve()` |
| `total_time` | Sum of both times | Calculated in pipeline |

**Example Timing**:
```
llm_time: 1.234s       → LLM query expansion
retrieval_time: 0.087s  → Dense + Sparse + Fusion
total_time: 1.321s      → Complete V2 pipeline
```

---

## 5. Web Application Integration

### 5.1 Endpoint Structure

| Endpoint | Purpose | Pipeline |
|----------|---------|----------|
| `/` | V2 Dashboard (main UI) | V2 |
| `/v2` | V2 Dashboard (explicit) | V2 |
| `/v2/query` | Single query processing | V2 |
| `/v2/bulk-query` | Bulk evaluation with progress tracking | V2 |
| `/v2/progress` | Real-time bulk progress | V2 |
| `/v2/session-info` | Latest session ID | V2 |
| `/history/v2` | All V2 sessions list | V2 |
| `/history/v2/<id>` | V2 session detail with metrics | V2 |

### 5.2 Database Schema

**File**: `rag_history_v2.db` (SQLite)

```sql
CREATE TABLE history_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id TEXT,
    original_query TEXT,           -- Original user query
    expanded_query TEXT,           -- LLM-expanded query
    dense_results TEXT,            -- JSON array
    sparse_results TEXT,           -- JSON array
    hybrid_results TEXT,           -- JSON array
    ground_truth TEXT,             -- JSON array of control IDs
    dense_hit REAL,
    sparse_hit REAL,
    hybrid_hit REAL,
    dense_recall REAL,
    sparse_recall REAL,
    hybrid_recall REAL,
    dense_precision REAL,
    sparse_precision REAL,
    hybrid_precision REAL,
    dense_mrr REAL,
    sparse_mrr REAL,
    hybrid_mrr REAL,
    llm_time REAL,               -- Query expansion time
    retrieval_time REAL,          -- Hybrid retrieval time
    total_time REAL,             -- Total pipeline time
    session_id INTEGER,
    method_order TEXT,            -- JSON array
    method_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Additions vs V1**:
- `expanded_query` column stores LLM-expanded query
- `llm_time` column stores query expansion duration
- `retrieval_time` column stores hybrid retrieval duration

### 5.3 UI Components

#### Main Dashboard (`/v2`)
- Single query input with ground truth
- Bulk input for batch evaluation
- Session management (new/continue)
- Real-time progress bar for bulk operations
- Results display with:
  - Original query
  - Expanded query
  - Dense/Sparse/Hybrid results
  - Metrics (Hit@3, Recall@3, Precision@3, MRR)
  - Timings (LLM, Retrieval, Total)

#### History View (`/history/v2/<session_id>`)
- Overall performance summary table
- Per-query detailed table
- Modal popups for:
  - Original query (clickable)
  - Expanded query (clickable)
  - Control details
- Metrics per query

### 5.4 Performance Section Design

**Overall Performance Table** (at `/history/v2/<session_id>`):

| Method | Hit@3 | Recall@3 | Precision@3 | MRR | LLM Time | Retrieval Time | Total Time |
|--------|--------|-----------|--------------|-----|----------|----------------|------------|
| Query Expansion | 0.833 | 0.750 | 0.250 | 0.667 | 1.234s | 0.087s | 1.321s |

**Per-Query Table**:

| ID | Original Query | Query Expansion | Hybrid (Top-3) | Ground Truth | Metrics | Time |
|----|---------------|-----------------|-----------------|--------------|----------|------|
| Q1 | "Login tanpa..." | "Login tanpa..." | A.5.15, A.5.18, A.5.1 | ["A.5.18"] | H:1.00 R:1.00... | LLM:1.234s<br>Retr:0.087s<br>Total:1.321s |

**Interactive Features**:
- Click "Original Query" → Full text modal
- Click "Query Expansion" → Full text modal
- Click control ID → Control detail modal (title, objective, description)

---

## 6. Technical Details

### 6.1 Function Call Flow

```
User submits query via /v2
    ↓
Flask route handler (/v2/query)
    ↓
rag_pipeline_v2.run(query, k=3)
    ↓
query_expansion(query)
    ├── build_expansion_prompt(query)
    ├── call_ollama_expand(prompt) → Ollama API
    └── Return {original_query, expanded_query, llm_time}
    ↓
HybridRetriever.retrieve(expanded_query, k=3)  [REUSED FROM V1]
    ├── Dense: encode → dot product → top-k
    ├── Sparse: BM25 scoring → top-k
    ├── Hybrid: normalize → weighted sum fusion → top-k
    └── Return {dense_results, sparse_results, hybrid_results, timings}
    ↓
RAGPipelineV2.build.build_prompt(original_query, hybrid_results)
    └── Final prompt with retrieved context
    ↓
generate_answer(prompt)  [REUSED FROM V1 LLM WRAPPER]
    └── Ollama API → JSON extraction
    ↓
Return complete result to Flask
    ↓
Flask saves to SQLite (rag_history_v2.db)
    ↓
UI displays results with timings and metrics
```

### 6.2 Integration Points with V1

| V1 Component | V2 Usage | Import Location |
|--------------|------------|-----------------|
| `HybridRetriever` | Main retrieval engine | `from hybrid.hybrid_retriever import HybridRetriever` |
| `generate_answer()` | Final LLM generation | `from llm.llm_wrapper import generate_answer` |
| `prompt_template.txt` | System prompt for generation | V1 prompts directory |
| `iso_controls.json` | Control corpus | V1 data directory |
| BM25 logic | Sparse retrieval | Used via HybridRetriever |

### 6.3 Latency Implications

**V1 Latency**:
- Single retrieval: ~0.050–0.150s
- LLM generation: ~0.500–2.000s
- Total: ~0.550–2.150s

**V2 Latency**:
- Query expansion (LLM): ~0.500–2.500s
- Retrieval: ~0.050–0.150s
- LLM generation: ~0.500–2.000s
- Total: ~1.050–4.650s

**Trade-off**:
- V2 adds **~0.5–2.5s latency** due to query expansion
- Benefit: Potentially higher retrieval accuracy
- Mitigation: Expansion LLM uses temperature=0.0 for consistency

---

## 7. Usage Examples

### 7.1 Start V2 Application

```bash
cd D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2
python app\app.py
```

**Output**:
```
 * Running on http://127.0.0.1:5001
 * Press CTRL+C to quit
```

### 7.2 Single Query via API

**Request**:
```bash
curl -X POST http://127.0.0.1:5001/v2/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Sistem autentikasi pengguna menggunakan password yang mudah ditebak",
    "ground_truth_ranked": ["A.5.18", "A.5.16"]
  }'
```

**Response**:
```json
{
  "original_query": "Sistem autentikasi pengguna menggunakan password yang mudah ditebak",
  "expanded_query": "Sistem autentikasi pengguna menggunakan password yang mudah ditebak, kata sandi lemah, kerentanan otentikasi, kebijakan kata sandi, pengelolaan kredensial, akses tidak sah",
  "dense_results": [...],
  "sparse_results": [...],
  "hybrid_results": [
    {
      "control_id": "A.5.18",
      "title": "Penggunaan kata sandi yang benar",
      "score": 0.8234
    }
  ],
  "metrics": {
    "hybrid": {
      "hit": 1.0,
      "recall": 1.0,
      "precision": 1.0,
      "mrr": 1.0
    }
  },
  "timings": {
    "llm_time": 1.234,
    "retrieval_time": 0.087,
    "total_time": 1.321
  }
}
```

### 7.3 Bulk Evaluation

**Input** (`evaluation/test_queries.json`):
```json
[
  {
    "query_id": "Q1",
    "query": "Login tanpa autentikasi dua faktor",
    "ground_truth_ranked": ["A.5.15", "A.5.18", "A.5.1"]
  },
  {
    "query_id": "Q2",
    "query": "Dokumen kebijakan keamanan tidak disetujui manajemen",
    "ground_truth_ranked": ["A.5.1"]
  }
]
```

**Request**:
```bash
curl -X POST http://127.0.0.1:5001/v2/bulk-query \
  -H "Content-Type: application/json" \
  -d '{
    "items": [...],
    "method_order": ["dense", "sparse", "hybrid"],
    "session_mode": "new"
  }'
```

**Response**:
```json
{
  "message": "Bulk processing started",
  "status": "started",
  "session_id": 1,
  "method_order": ["dense", "sparse", "hybrid"],
  "single_method": false
}
```

---

## 8. Advantages Over V1

### 8.1 Retrieval Quality
- **Semantic Enhancement**: LLM adds relevant technical terms (synonyms, related concepts)
- **Better Coverage**: Expanded queries match controls that original query might miss
- **Domain Knowledge**: LLM knows ISO 27001:2022 terminology

### 8.2 Research Value
- **Controlled Experiment**: Clean separation between V1 and V2 for thesis comparison
- **Traceable Pipeline**: Clear timing breakdown per stage
- **Reproducibility**: Deterministic LLM (temperature=0.0)

### 8.3 User Experience
- **Transparent Process**: UI shows original vs expanded query
- **Performance Metrics**: Detailed timing for each stage
- **Interactive Inspection**: Clickable popups for queries and controls

---

## 9. Limitations

### 9.1 Latency Overhead
- Additional LLM call adds ~0.5–2.5s per query
- May impact real-time applications

### 9.2 LLM Dependency
- Requires Ollama running with `qwen2.5:3b` model
- Fallback to original query on LLM failure

### 9.3 Expansion Quality
- LLM may over-expand or drift from original intent
- No semantic validation of expanded query
- Potential for redundant terms in expansion

### 9.4 Determinism
- Temperature=0.0 ensures consistency, but LLM may still vary across runs
- Expansion results should be logged for reproducibility

---

## 10. Comparison Summary

| Dimension | V1 | V2 |
|-----------|-----|-----|
| **Pipeline** | Direct retrieval | Expansion → Retrieval |
| **Query Processing** | Raw query | LLM-expanded query |
| **LLM Calls** | 1 (generation) | 2 (expansion + generation) |
| **Avg Latency** | ~1.0s | ~2.5s |
| **Retrieval Source** | Original query | Expanded query |
| **Modules** | Single pipeline | Modular (expansion + V1 reuse) |
| **Complexity** | Simple | Medium |
| **Research Value** | Baseline | Enhanced baseline |

---

## 11. Future Enhancements (Not in Current Scope)

- **Query Expansion Validation**: Check if expansion maintains semantic similarity
- **Multiple Expansion Strategies**: Compare different prompt templates
- **Expansion Parameter Tuning**: Temperature, max tokens experimentation
- **Hybrid Expansion**: Combine LLM expansion with rule-based expansion
- **Caching**: Cache expansion results for repeated queries

---

## 12. References

- V1 Documentation: `D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\baselineRAGv1.md`
- V1 Specification: `D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\RAG_V1_Spec.md`
- Master Context: `D:\Hilmi\Coding\MasterFolderSkripsi\skripsimastercontext.md`

---

**Last Updated**: 2026-04-26
**Version**: 2.0
**Status**: Complete and tested