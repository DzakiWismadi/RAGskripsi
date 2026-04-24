# embedding/build_index.py
# Builds FAISS index from ISO control embeddings

import os
import sys
import json
import numpy as np
import faiss

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from embedding.embedding_model import encode_control, EMBEDDING_DIM, MODEL_NAME

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CONTROLS_PATH = os.path.join(DATA_DIR, "iso_controls.json")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(DATA_DIR, "index_metadata.json")


def build_index():
    # Load controls
    print(f"Loading controls from {CONTROLS_PATH}")
    with open(CONTROLS_PATH, "r", encoding="utf-8") as f:
        controls = json.load(f)
    print(f"Loaded {len(controls)} controls")

    # Encode all controls
    print("Encoding controls...")
    all_embeddings = []
    for i, ctrl in enumerate(controls):
        emb = encode_control(ctrl)
        all_embeddings.append(emb)
        if (i + 1) % 10 == 0:
            print(f"  Encoded {i + 1}/{len(controls)}")

    embeddings_matrix = np.vstack(all_embeddings).astype(np.float32)
    print(f"Embeddings shape: {embeddings_matrix.shape}")

    # Verify normalization
    norms = np.linalg.norm(embeddings_matrix, axis=1)
    print(f"Norm range: [{norms.min():.6f}, {norms.max():.6f}] (should be ~1.0)")

    # Build FAISS IndexFlatIP (cosine similarity via normalized vectors)
    print("Building FAISS IndexFlatIP index...")
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings_matrix)
    print(f"Index total vectors: {index.ntotal}")

    # Save index
    faiss.write_index(index, INDEX_PATH)
    print(f"Index saved to {INDEX_PATH}")

    # Save metadata
    metadata = {
        "model_name": MODEL_NAME,
        "embedding_dim": EMBEDDING_DIM,
        "num_controls": len(controls),
        "control_ids": [ctrl["control_id"] for ctrl in controls],
        "index_type": "IndexFlatIP",
        "normalization": "L2-normalized (cosine similarity via inner product)",
    }
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved to {METADATA_PATH}")

    print("\nBuild complete!")
    return index, metadata


if __name__ == "__main__":
    build_index()
