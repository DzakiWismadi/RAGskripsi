print("Testing cross-encoder models...")
import os
os.environ["HF_HUB_OFFLINE"] = "1"  # avoid download if cached

# Check what models are cached locally
from pathlib import Path
cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
if cache_dir.exists():
    models = [d.name for d in cache_dir.iterdir() if d.is_dir()]
    print("Cached models:")
    for m in sorted(models):
        print(f"  {m}")
else:
    print("No HF cache directory found")

# Test loading the current cross-encoder
print("\nLoading cross-encoder/ms-marco-MiniLM-L-6-v2...")
from sentence_transformers import CrossEncoder
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print(f"Model loaded: {model.config.model_type}")
print(f"Max length: {model.config.max_length}")

# Test with a bilingual query
query = "Tidak ada prosedur pencadangan data yang dilakukan secara berkala"
doc1 = "Pencadangan informasi | objective... | Prosedur harus..."
doc2 = "Kontrol akses | objective... | Akses harus..."
scores = model.predict([(query, doc1), (query, doc2)])
print(f"\nBilingual test:")
print(f"  Relevant doc score: {scores[0]:.4f}")
print(f"  Irrelevant doc score: {scores[1]:.4f}")
print(f"  Correct order: {scores[0] > scores[1]}")
