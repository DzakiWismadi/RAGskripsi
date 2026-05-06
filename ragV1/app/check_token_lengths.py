import sys, json
sys.path.insert(0, r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1')
sys.path.insert(0, r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV3')

from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print(f"Max length: {model.model.config.max_position_embeddings}")
print(f"Tokenizer max length: {model.tokenizer.model_max_length}")

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

ctrl_map = {c['control_id']: c for c in controls}

def doc_to_rerank_text(doc):
    parts = []
    title = str(doc.get("title", "")).strip()
    if title:
        parts.append(title)
    objective = str(doc.get("objective", "")).strip()
    if objective:
        parts.append(objective)
    description = str(doc.get("description", "")).strip()
    if description:
        parts.append(description)
    keywords_en = doc.get("keywords_en", [])
    if keywords_en:
        parts.append("Keywords EN: " + " ".join(str(k) for k in keywords_en))
    keywords_id = doc.get("keywords_id", [])
    if keywords_id:
        parts.append("Kata kunci ID: " + " ".join(str(k) for k in keywords_id))
    audit_indicators = doc.get("audit_indicators_en", []) or doc.get("audit_indicators_id", [])
    if audit_indicators:
        parts.append("Audit indicators: " + " ".join(str(a) for a in audit_indicators))
    return " | ".join(parts)

query = "Tidak terdapat monitoring terhadap aktivitas pengguna dalam sistem."
targets = ['A.8.15', 'A.8.34', 'A.8.16', 'A.8.3']

for cid in targets:
    c = ctrl_map[cid]
    text = doc_to_rerank_text(c)
    tokens = model.tokenizer(query, text, truncation=False)
    print(f"\n{cid} - {c['title']}")
    print(f"  Doc text length: {len(text)} chars")
    print(f"  Token count (query+doc): {len(tokens['input_ids'])}")
    print(f"  Truncated: {'YES' if len(tokens['input_ids']) > 512 else 'NO'}")
