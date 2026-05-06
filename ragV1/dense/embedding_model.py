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
    """
    Convert ISO control to searchable text for embedding.
    Includes original fields plus semantic enrichment for better retrieval.
    """
    parts = [
        control.get('title', ''),
        control.get('objective', ''),
        control.get('description', ''),
    ]
    
    # Add enriched keywords for better semantic matching
    keywords_en = control.get('keywords_en', [])
    keywords_id = control.get('keywords_id', [])
    if keywords_en or keywords_id:
        parts.append(' '.join(keywords_en))
        parts.append(' '.join(keywords_id))
    
    # Add audit indicators (crucial for finding relevant controls from audit findings)
    audit_indicators_en = control.get('audit_indicators_en', [])
    audit_indicators_id = control.get('audit_indicators_id', [])
    if audit_indicators_en or audit_indicators_id:
        parts.append(' '.join(audit_indicators_en))
        parts.append(' '.join(audit_indicators_id))
    
    # Add related assets for asset-specific queries
    related_assets_en = control.get('related_assets_en', [])
    related_assets_id = control.get('related_assets_id', [])
    if related_assets_en or related_assets_id:
        parts.append(' '.join(related_assets_en))
        parts.append(' '.join(related_assets_id))
    
    # Add security principles
    security_principles_en = control.get('security_principles_en', [])
    security_principles_id = control.get('security_principles_id', [])
    if security_principles_en or security_principles_id:
        parts.append(' '.join(security_principles_en))
        parts.append(' '.join(security_principles_id))
    
    return ' | '.join(parts)

