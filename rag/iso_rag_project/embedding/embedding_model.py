# embedding/embedding_model.py
# Singleton loader for paraphrase-multilingual-MiniLM-L12-v2 (384-dim)
# Supports Indonesian text for ISO 27001 RAG audit mapping

import os
import random
import logging
import numpy as np

# Fix seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

try:
    import torch
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
except ImportError:
    pass

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

_model = None


def get_model() -> SentenceTransformer:
    """Singleton loader for the embedding model."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        log_version_info()
    return _model


def encode_texts(texts: list[str]) -> np.ndarray:
    """
    Encode a list of texts into L2-normalized float32 embeddings.

    Args:
        texts: List of strings to encode.

    Returns:
        np.ndarray of shape (len(texts), 384), L2-normalized, float32.
    """
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    embeddings = embeddings.astype(np.float32)
    # L2 normalize for cosine similarity via inner product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    embeddings = embeddings / norms
    return embeddings


def encode_control(control: dict) -> np.ndarray:
    """
    Encode a single ISO control by concatenating title | objective | description.

    Args:
        control: Dict with 'title', 'objective', 'description' keys.

    Returns:
        np.ndarray of shape (1, 384), L2-normalized, float32.
    """
    text = f"{control['title']} | {control['objective']} | {control['description']}"
    return encode_texts([text])


def log_version_info():
    """Log version info for reproducibility (MasterPrompt #15)."""
    import sentence_transformers
    model = get_model()
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"sentence-transformers version: {sentence_transformers.__version__}")
    logger.info(f"Embedding dimension: {EMBEDDING_DIM}")
    logger.info(f"Max sequence length: {model.max_seq_length}")
    logger.info(f"Random seed: {SEED}")
    print(f"[EmbeddingModel] Model: {MODEL_NAME}")
    print(f"[EmbeddingModel] sentence-transformers: {sentence_transformers.__version__}")
    print(f"[EmbeddingModel] Dimension: {EMBEDDING_DIM}")
    print(f"[EmbeddingModel] Max seq length: {model.max_seq_length}")
    print(f"[EmbeddingModel] Seed: {SEED}")
