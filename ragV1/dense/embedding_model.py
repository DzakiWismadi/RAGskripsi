import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_embedding_dim() -> int:
    return int(get_model().get_sentence_embedding_dimension())


def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms


def encode_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    embeddings = embeddings.astype(np.float32)
    return normalize(embeddings)


def control_to_text(control: dict) -> str:
    return f"{control['title']} | {control['objective']} | {control['description']}"

