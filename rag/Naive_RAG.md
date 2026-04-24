# RAG Legacy Pipeline — End-to-End Explanation (A1–D3)

Dokumen ini menjelaskan alur lengkap RAG (Retrieval-Augmented Generation) pada sistem Legacy secara **end-to-end**, dilengkapi dengan:

* Contoh konkret
* Transformasi data (text → vector → similarity → reasoning → JSON)
* Mapping ke source code (file & function)

---

# 🔎 CONTEXT CONTOH

## Input Query (B1)

```
"Seluruh komponen server, kontainer, dan kunci aplikasi tercatat dalam katalog aset teknis yang terintegrasi dengan pipeline deployment."
```

---

# 🟦 A1 — ISO Controls JSON (Knowledge Source)

## 📂 Source files:

* `data/iso_controls.json`
* `embedding/build_index.py`
* `retrieval/retrieve.py`

## 📥 Contoh data:

```json
[
  {
    "id": "A.5.9",
    "title": "Inventory of information assets",
    "objective": "Assets should be identified",
    "description": "All assets must be recorded and managed."
  }
]
```

## ⚙️ Proses:

* JSON dibaca ke memory sebagai Python objects
* Tidak menggunakan database (file-based)

## 📌 Peran:

Single source of truth untuk knowledge base

---

# 🟦 A2 — Text Extraction (Control → Text)

## 📂 Source files:

* `embedding/embedding_model.py` → `encode_control()`
* `embedding/build_index.py`

## 📥 Transformasi:

```python
text = f"{title} | {objective} | {description}"
```

## 📤 Output:

```
"A.5.9 | Inventory of information assets | Assets should be identified | All assets must be recorded and managed."
```

## ⚙️ Proses:

* Menggabungkan 3 field (title, objective, description)
* 1 control = 1 semantic unit

## 📌 Peran:

Membentuk input embedding yang kaya konteks

---

# 🟦 A3 — Embedding (SentenceTransformer)

## 📂 Source files:

* `embedding/embedding_model.py`

  * `get_model()`
  * `encode_control()`
  * `encode_texts()`

## 🤖 Model:

```
paraphrase-multilingual-MiniLM-L12-v2
```

## 📥 Input:

```
"A.5.9 | Inventory ... managed."
```

## 📤 Output (contoh):

```python
A.5.9_vector = [0.12, -0.33, 0.89, ..., 0.07]
```

## ⚙️ Proses:

```python
vector = model.encode(text)
vector = normalize(vector)
```

## 📌 Properti:

* float32
* dimensi 384
* normalized (||v|| = 1)

## 📌 Peran:

Representasi numerik untuk semantic similarity

---

# 🟦 A4 — Vector Storage (FAISS)

## 📂 Source files:

* `embedding/build_index.py`
* `retrieval/retrieve.py`
* `data/faiss_index.bin`
* `data/index_metadata.json`

## 📥 Input:

```python
[vectors]
```

## ⚙️ Proses:

```python
index = faiss.IndexFlatIP(dim=384)
index.add(vectors)
faiss.write_index(index, "faiss_index.bin")
```

## 📤 Output:

### faiss_index.bin

Binary file berisi vector

### index_metadata.json

```json
{
  "0": "A.5.9",
  "1": "A.8.12"
}
```

## 📌 Peran:

Mapping vector index → control_id

---

# 🟨 B1 — User Query Input

## 📂 Source files:

* `rag/rag_pipeline.py`
* `query.py`

## 📥 Input:

```
"Seluruh komponen server ... katalog aset teknis ..."
```

## ⚙️ Proses:

* Input diterima sebagai string
* Tidak ada query rewriting

## 📌 Peran:

Entry point pipeline

---

# 🟨 B2 — Query Embedding

## 📂 Source files:

* `retrieval/retrieve.py`
* `embedding/embedding_model.py`

## 📤 Output:

```python
query_vector = [0.11, -0.29, 0.91, ..., 0.05]
```

## ⚙️ Proses:

```python
query_embedding = encode_texts([query])
```

## 📌 Peran:

Menjaga konsistensi vector space

---

# 🟨 B3 — Query Vector

## 📂 Source files:

* `retrieval/retrieve.py`

## 📌 Bentuk:

```python
(1, 384)
```

## ⚙️ Digunakan:

```python
index.search(query_vector, k)
```

---

# 🟩 C1 — Similarity Computation

## 📂 Source files:

* `retrieval/retrieve.py`

## ⚙️ Proses:

```python
scores, indices = index.search(query_vector, k)
```

## 📤 Output:

```python
scores = [0.87, 0.42]
indices = [0, 1]
```

## 📌 Penjelasan:

* Inner product digunakan
* Equivalent ke cosine similarity

---

# 🟩 C2 — Top-K Selection

## 📂 Source files:

* `retrieval/retrieve.py`

## 📤 Output:

```json
[
  {"id": "A.5.9", "score": 0.87},
  {"id": "A.8.12", "score": 0.42}
]
```

## 📌 Peran:

Filtering sebelum LLM

---

# 🟪 D1 — LLM Context Injection

## 📂 Source files:

* `rag/rag_pipeline.py`
* `llm/prompt_template.txt`

## 📤 Prompt:

```
Audit statement:
...
Relevant controls:
...
Return JSON only
```

## 📌 Peran:

Menggabungkan query + context

---

# 🟪 D2 — Reasoning & Classification

## 📂 Source files:

* `llm/llm_wrapper.py`

## ⚙️ Proses:

* Prompt dikirim ke Ollama
* Model melakukan reasoning dan classification

---

# 🟪 D3 — Structured Output

## 📂 Source files:

* `llm/llm_wrapper.py`
* `rag/rag_pipeline.py`

## 📤 Output:

```json
{
  "control_id": "A.5.9",
  "applicable": "Yes",
  "implementation_status": "Implemented",
  "justification": "...",
  "recommendation": "...",
  "retrieved_controls": [
    {"id": "A.5.9", "score": 0.87},
    {"id": "A.8.12", "score": 0.42}
  ]
}
```

## ⚙️ Proses:

* Extract JSON
* Validasi schema

---

# 🔥 FINAL INSIGHT

Pipeline ini adalah **Naive RAG**:

* ✅ Embedding-based retrieval
* ❌ No query rewriting
* ❌ No reranking
* ❌ No hybrid retrieval

Flow:

```
text → embedding → similarity → top-k → LLM → JSON
```

---

# 🚀 Kesimpulan

Dokumen ini bisa digunakan untuk:

* Code tracing
* Verifikasi implementasi
* Dokumentasi skripsi (Bab 3 / Bab 4)
