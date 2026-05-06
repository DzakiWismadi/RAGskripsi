from typing import Any
import numpy as np

from sentence_transformers import CrossEncoder

# ── Model selection ──────────────────────────────────────────────────────────────
# BAAI/bge-reranker-v2-m3: multilingual (100+ languages including Indonesian),
# trained on diverse relevance data.  Much better than ms-marco for non-English.
MODEL_NAME = "BAAI/bge-reranker-v2-m3"
MODEL_NAME_MINILM = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model: CrossEncoder | None = None
_model_minilm: CrossEncoder | None = None


def get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME)
    return _model


def get_model_minilm() -> CrossEncoder:
    global _model_minilm
    if _model_minilm is None:
        _model_minilm = CrossEncoder(MODEL_NAME_MINILM)
    return _model_minilm


# ── Document text for cross-encoder input ───────────────────────────────────────
# Enrich the text with keywords and audit indicators so the cross-encoder has
# more semantic signal for the cybersecurity / ISO 27001 domain.
def _doc_to_rerank_text(doc: dict[str, Any]) -> str:
    parts: list[str] = []

    title = str(doc.get("title", "")).strip()
    if title:
        parts.append(title)

    objective = str(doc.get("objective", "")).strip()
    if objective:
        parts.append(objective)

    description = str(doc.get("description", "")).strip()
    if description:
        parts.append(description)

    # Enrichment fields — provide denser semantic signal
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


# ── Hybrid rerank score ─────────────────────────────────────────────────────────
# Combines cross-encoder relevance score with original hybrid retrieval score.
# This prevents the cross-encoder from completely overriding good retrieval
# signals, especially important when the CE model is not domain-specific.
ALPHA = 0.8  # weight for cross-encoder score
# (1 - ALPHA) = 0.2 weight goes to the normalized hybrid score


def _normalize(arr: np.ndarray) -> np.ndarray:
    """Min-max normalization to [0, 1]."""
    mn, mx = float(np.min(arr)), float(np.max(arr))
    if mx - mn < 1e-12:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


def rerank_with_model(
    model: CrossEncoder,
    query: str,
    retrieved_docs: list[dict[str, Any]],
    top_n: int | None = None,
    alpha: float | None = None,
) -> list[dict[str, Any]]:
    if not retrieved_docs:
        return []

    _alpha = alpha if alpha is not None else ALPHA

    pairs = [(query, _doc_to_rerank_text(doc)) for doc in retrieved_docs]
    ce_scores = np.array(model.predict(pairs, show_progress_bar=False), dtype=np.float32)

    hybrid_scores = np.array(
        [float(doc.get("hybrid_score", 0.0)) for doc in retrieved_docs],
        dtype=np.float32,
    )

    ce_norm = _normalize(ce_scores)
    hybrid_norm = _normalize(hybrid_scores)
    combined = _alpha * ce_norm + (1 - _alpha) * hybrid_norm

    ranked = []
    for i, doc in enumerate(retrieved_docs):
        item = dict(doc)
        item["rerank_score"] = float(ce_scores[i])
        item["rerank_score_norm"] = float(ce_norm[i])
        item["hybrid_score_norm"] = float(hybrid_norm[i])
        item["combined_score"] = float(combined[i])
        ranked.append(item)

    ranked.sort(key=lambda x: x["combined_score"], reverse=True)

    if top_n is not None:
        return ranked[: max(int(top_n), 0)]
    return ranked


def rerank_documents(
    query: str,
    retrieved_docs: list[dict[str, Any]],
    top_n: int | None = None,
    alpha: float | None = None,
) -> list[dict[str, Any]]:
    return rerank_with_model(get_model(), query, retrieved_docs, top_n, alpha)


def rerank_documents_minilm(
    query: str,
    retrieved_docs: list[dict[str, Any]],
    top_n: int | None = None,
    alpha: float | None = None,
) -> list[dict[str, Any]]:
    return rerank_with_model(get_model_minilm(), query, retrieved_docs, top_n, alpha)
