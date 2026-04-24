# retrieval/retrieve.py
# Retrieves top-k ISO controls from FAISS index given a query sentence

import os
import sys
import json
import numpy as np
import faiss

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from embedding.embedding_model import encode_texts

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(DATA_DIR, "index_metadata.json")
CONTROLS_PATH = os.path.join(DATA_DIR, "iso_controls.json")

# Singleton cache
_index = None
_metadata = None
_controls = None


def _load_index():
    """Load FAISS index, metadata, and controls (cached after first call)."""
    global _index, _metadata, _controls
    if _index is None:
        _index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
        with open(CONTROLS_PATH, "r", encoding="utf-8") as f:
            _controls = json.load(f)
    return _index, _metadata, _controls


def retrieve_top_k(query: str, k: int = 3) -> list[dict]:
    """
    Retrieve the top-k most similar ISO controls for a query sentence.

    Args:
        query: Audit sentence in Indonesian.
        k: Number of results to return.

    Returns:
        List of dicts with keys: control_id, title, description, similarity_score.
    """
    index, metadata, controls = _load_index()

    query_embedding = encode_texts([query])
    scores, indices = index.search(query_embedding, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        ctrl = controls[idx]
        results.append({
            "control_id": ctrl["control_id"],
            "title": ctrl["title"],
            "objective": ctrl["objective"],
            "description": ctrl["description"],
            "similarity_score": float(score),
        })
    return results


def retrieve_top3(query: str) -> list[dict]:
    """Convenience wrapper returning top-3 results (thesis constraint)."""
    return retrieve_top_k(query, k=3)


def format_retrieved_for_prompt(controls: list[dict]) -> str:
    """
    Format retrieved controls as text for LLM prompt injection.

    Args:
        controls: List of retrieved control dicts from retrieve_top_k.

    Returns:
        Formatted string for inclusion in LLM prompt.
    """
    lines = []
    for i, ctrl in enumerate(controls, 1):
        desc = ctrl['description']
        # Truncate description to first 150 chars for prompt brevity
        if len(desc) > 150:
            desc = desc[:150] + "..."
        lines.append(f"{i}. {ctrl['control_id']} - {ctrl['title']}: {desc}")
        lines.append("")
    return "\n".join(lines)
