import json
import importlib.util
import math
import sqlite3
import sys
import threading
import time
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.rag_pipeline import RAGPipeline

app = Flask(__name__)
pipeline = RAGPipeline(project_root=PROJECT_ROOT)
V3_ROOT = PROJECT_ROOT.parent / "ragV3"
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))

v3_spec = importlib.util.spec_from_file_location("rag_pipeline_v3_module", V3_ROOT / "pipeline" / "rag_pipeline_v3.py")
if v3_spec is None or v3_spec.loader is None:
    raise RuntimeError("Unable to load RAG V3 pipeline module")
v3_module = importlib.util.module_from_spec(v3_spec)
v3_spec.loader.exec_module(v3_module)
RAGPipelineV3 = v3_module.RAGPipelineV3
pipeline_v3 = RAGPipelineV3(project_root=V3_ROOT)


DB_PATH = PROJECT_ROOT / "rag_history.db"
TOP_K = 3
HISTORY_LIMIT = 300
DEFAULT_METHOD_ORDER = ["dense", "sparse", "hybrid"]
VALID_METHODS = set(DEFAULT_METHOD_ORDER)

PROGRESS_STATE = {
    "current": 0,
    "total": 0,
    "percentage": 0,
    "running": False,
    "status": "idle",
    "started_at": None,
    "finished_at": None,
    "error": None,
    "bulk_results": [],
    "session_id": None,
    "method_order": list(DEFAULT_METHOD_ORDER),
    "queue_index": None,
    "queue_total": None,
    "queue_label": None,
}
PROGRESS_LOCK = threading.Lock()
BULK_THREAD = None
V3_BULK_THREAD = None

V3_QUEUE: list[dict[str, Any]] = []
V3_QUEUE_LOCK = threading.Lock()
V3_QUEUE_FILE = PROJECT_ROOT / "v3_queue.json"
V3_QUEUE_SESSION_COUNTER = 0


def _load_v3_queue() -> None:
    global V3_QUEUE, V3_QUEUE_SESSION_COUNTER
    if V3_QUEUE_FILE.exists():
        try:
            data = json.loads(V3_QUEUE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                V3_QUEUE = data.get("items", [])
                saved_counter = data.get("session_counter", 0)
            elif isinstance(data, list):
                V3_QUEUE = data
                saved_counter = 0
            else:
                V3_QUEUE = []
                saved_counter = 0
        except (OSError, json.JSONDecodeError):
            V3_QUEUE = []
            saved_counter = 0
    else:
        saved_counter = 0
    db_latest = get_latest_v3_session_id()
    if db_latest is not None:
        V3_QUEUE_SESSION_COUNTER = max(saved_counter, db_latest)
    else:
        V3_QUEUE_SESSION_COUNTER = saved_counter


def _save_v3_queue() -> None:
    with V3_QUEUE_LOCK:
        data = {"items": V3_QUEUE, "session_counter": V3_QUEUE_SESSION_COUNTER}
        V3_QUEUE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def set_progress(current: int, total: int, status: str, running: bool, error: str = None) -> None:
    percentage = int((current / total) * 100) if total > 0 else 0
    with PROGRESS_LOCK:
        PROGRESS_STATE["current"] = current
        PROGRESS_STATE["total"] = total
        PROGRESS_STATE["percentage"] = percentage
        PROGRESS_STATE["status"] = status
        PROGRESS_STATE["running"] = running
        PROGRESS_STATE["error"] = error
        if running and PROGRESS_STATE["started_at"] is None:
            PROGRESS_STATE["started_at"] = time.time()
            PROGRESS_STATE["finished_at"] = None
        if not running:
            PROGRESS_STATE["finished_at"] = time.time()


def reset_progress(total: int, session_id: int | None, method_order: list[str]) -> None:
    with PROGRESS_LOCK:
        PROGRESS_STATE["current"] = 0
        PROGRESS_STATE["total"] = total
        PROGRESS_STATE["percentage"] = 0
        PROGRESS_STATE["running"] = True
        PROGRESS_STATE["status"] = "starting"
        PROGRESS_STATE["started_at"] = time.time()
        PROGRESS_STATE["finished_at"] = None
        PROGRESS_STATE["error"] = None
        PROGRESS_STATE["bulk_results"] = []
        PROGRESS_STATE["session_id"] = session_id
        PROGRESS_STATE["method_order"] = list(method_order)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT,
                query TEXT,

                dense_results TEXT,
                sparse_results TEXT,
                hybrid_results TEXT,

                ground_truth TEXT,

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

                dense_time REAL,
                sparse_time REAL,
                hybrid_time REAL,
                total_time REAL,
                session_id INTEGER,
                method_order TEXT,
                method_name TEXT,

                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        for col_name, col_type in [
            ("query_id", "TEXT"),
            ("dense_results", "TEXT"),
            ("sparse_results", "TEXT"),
            ("hybrid_results", "TEXT"),
            ("ground_truth", "TEXT"),
            ("dense_hit", "REAL"),
            ("sparse_hit", "REAL"),
            ("hybrid_hit", "REAL"),
            ("dense_recall", "REAL"),
            ("sparse_recall", "REAL"),
            ("hybrid_recall", "REAL"),
            ("dense_precision", "REAL"),
            ("sparse_precision", "REAL"),
            ("hybrid_precision", "REAL"),
            ("dense_mrr", "REAL"),
            ("sparse_mrr", "REAL"),
            ("hybrid_mrr", "REAL"),
            ("dense_time", "REAL"),
            ("sparse_time", "REAL"),
            ("hybrid_time", "REAL"),
            ("total_time", "REAL"),
            ("session_id", "INTEGER"),
            ("method_order", "TEXT"),
            ("method_name", "TEXT"),
        ]:
            if not _column_exists(conn, "history", col_name):
                conn.execute(f"ALTER TABLE history ADD COLUMN {col_name} {col_type}")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history_v3 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT,
                query TEXT,
                hybrid_results TEXT,
                reranked_results TEXT,
                ground_truth TEXT,
                hybrid_hit REAL,
                hybrid_recall REAL,
                hybrid_precision REAL,
                hybrid_mrr REAL,
                reranking_hit REAL,
                reranking_recall REAL,
                reranking_precision REAL,
                reranking_mrr REAL,
                retrieval_time REAL,
                reranking_time REAL,
                total_time REAL,
                session_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        for col_name, col_type in [
            ("query_id", "TEXT"),
            ("query", "TEXT"),
            ("hybrid_results", "TEXT"),
            ("reranked_results", "TEXT"),
            ("ground_truth", "TEXT"),
            ("hybrid_hit", "REAL"),
            ("hybrid_recall", "REAL"),
            ("hybrid_precision", "REAL"),
            ("hybrid_mrr", "REAL"),
            ("reranking_hit", "REAL"),
            ("reranking_recall", "REAL"),
            ("reranking_precision", "REAL"),
            ("reranking_mrr", "REAL"),
            ("hybrid_ndcg", "REAL"),
            ("reranking_ndcg", "REAL"),
            ("hybrid_map", "REAL"),
            ("reranking_map", "REAL"),
            ("retrieval_time", "REAL"),
            ("reranking_time", "REAL"),
            ("total_time", "REAL"),
            ("session_id", "INTEGER"),
            ("params", "TEXT"),
        ]:
            if not _column_exists(conn, "history_v3", col_name):
                conn.execute(f"ALTER TABLE history_v3 ADD COLUMN {col_name} {col_type}")

        conn.commit()


def load_control_catalog() -> dict[str, dict[str, Any]]:
    # Use enriched controls for better retrieval
    controls_path = PROJECT_ROOT / "data" / "iso_controls_enriched.json"
    controls = json.loads(controls_path.read_text(encoding="utf-8"))
    return {
        item["control_id"]: {
            "title": item.get("title", ""),
            "objective": item.get("objective", ""),
            "description": item.get("description", ""),
            # Include enrichment fields for frontend display
            "keywords_en": item.get("keywords_en", []),
            "keywords_id": item.get("keywords_id", []),
            "audit_indicators_en": item.get("audit_indicators_en", []),
            "audit_indicators_id": item.get("audit_indicators_id", []),
            "related_assets_en": item.get("related_assets_en", []),
            "related_assets_id": item.get("related_assets_id", []),
            "security_principles_en": item.get("security_principles_en", []),
            "security_principles_id": item.get("security_principles_id", []),
        }
        for item in controls
    }


CONTROL_CATALOG = load_control_catalog()


def load_v3_ground_truth_by_query() -> dict[str, list[str]]:
    data_path = PROJECT_ROOT / "evaluation" / "test_queries.json"
    if not data_path.exists():
        return {}
    try:
        dataset = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(dataset, list):
        return {}

    out: dict[str, list[str]] = {}
    for item in dataset:
        if not isinstance(item, dict):
            continue
        query = str(item.get("query", "")).strip()
        ground_truth_raw = item.get("ground_truth", [])
        if not query or not isinstance(ground_truth_raw, list):
            continue
        out[query] = [str(x).strip() for x in ground_truth_raw if str(x).strip()]
    return out


V3_GROUND_TRUTH_BY_QUERY = load_v3_ground_truth_by_query()


def normalize_method_order(method_order: list[str] | None, expected_count: int | None = None) -> list[str]:
    order = [str(x).strip().lower() for x in (method_order or DEFAULT_METHOD_ORDER)]
    if not order:
        raise ValueError("method_order must not be empty")
    if any(name not in VALID_METHODS for name in order):
        raise ValueError("method_order can only contain dense, sparse, hybrid")
    if len(set(order)) != len(order):
        raise ValueError("method_order must not contain duplicate methods")
    if expected_count is not None and len(order) != expected_count:
        raise ValueError(f"method_order must contain exactly {expected_count} method(s)")
    if expected_count == 3 and set(order) != VALID_METHODS:
        raise ValueError("method_order must contain exactly dense, sparse, hybrid")
    return order


def get_latest_session_id() -> int | None:
    with get_db_connection() as conn:
        row = conn.execute("SELECT MAX(session_id) AS latest FROM history WHERE session_id IS NOT NULL").fetchone()
    latest = row["latest"] if row else None
    return int(latest) if latest is not None else None


def create_new_session() -> int:
    latest = get_latest_session_id()
    return 1 if latest is None else latest + 1


def resolve_session_id(mode: str) -> int:
    normalized = str(mode or "continue").strip().lower()
    if normalized == "new":
        return create_new_session()
    latest = get_latest_session_id()
    return latest if latest is not None else create_new_session()


def get_session_summaries() -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                session_id,
                COUNT(*) AS row_count,
                MIN(timestamp) AS started_at,
                MAX(timestamp) AS finished_at
            FROM history
            WHERE session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY session_id DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def get_legacy_history_count() -> int:
    with get_db_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM history WHERE session_id IS NULL").fetchone()
    return int(row["total"]) if row else 0


def get_latest_v3_session_id() -> int | None:
    with get_db_connection() as conn:
        row = conn.execute("SELECT MAX(session_id) AS latest FROM history_v3 WHERE session_id IS NOT NULL").fetchone()
    latest = row["latest"] if row else None
    return int(latest) if latest is not None else None


def create_new_v3_session() -> int:
    latest = get_latest_v3_session_id()
    return 1 if latest is None else latest + 1


def resolve_v3_session_id(mode: str) -> int:
    normalized = str(mode or "continue").strip().lower()
    if normalized == "new":
        return create_new_v3_session()
    latest = get_latest_v3_session_id()
    return latest if latest is not None else create_new_v3_session()


def get_v3_session_summaries() -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                session_id,
                COUNT(*) AS row_count,
                MIN(timestamp) AS started_at,
                MAX(timestamp) AS finished_at
            FROM history_v3
            WHERE session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY session_id DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def get_v3_legacy_history_count() -> int:
    with get_db_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM history_v3 WHERE session_id IS NULL").fetchone()
    return int(row["total"]) if row else 0


def compact_results(results: list[dict[str, Any]], score_key: str, k: int = TOP_K) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in (results or [])[:k]:
        compact.append(
            {
                "control_id": item.get("control_id", ""),
                "title": item.get("title", ""),
                "objective": item.get("objective", ""),
                "description": item.get("description", ""),
                "score": float(item.get(score_key, 0.0)),
            }
        )
    return compact


def compute_metrics(predicted_ids: list[str], ground_truth_ranked: list[str], k: int = TOP_K) -> dict[str, float | None]:
    gt = [str(x).strip() for x in ground_truth_ranked if str(x).strip()]
    pred = [str(x).strip() for x in predicted_ids[:k] if str(x).strip()]

    if not gt:
        return {"hit": None, "recall": None, "precision": None, "mrr": None, "ndcg": None, "map": None}

    inter_count = 0
    seen: set[str] = set()
    for cid in pred:
        if cid in gt and cid not in seen:
            inter_count += 1
            seen.add(cid)

    hit = 1.0 if inter_count > 0 else 0.0
    recall = inter_count / max(len(gt), 1)
    precision = inter_count / max(k, 1)

    first_rank = 0
    for idx, cid in enumerate(pred, start=1):
        if cid in gt:
            first_rank = idx
            break
    mrr = 1.0 / first_rank if first_rank > 0 else 0.0

    gt_set = set(gt)
    dcg = 0.0
    for idx, cid in enumerate(pred, start=1):
        if cid in gt_set:
            dcg += 1.0 / math.log2(idx + 1)
    ideal_hits = min(len(gt), k)
    idcg = 0.0
    for rank in range(1, ideal_hits + 1):
        idcg += 1.0 / math.log2(rank + 1)
    ndcg = dcg / idcg if idcg > 0 else 0.0

    # MAP@k — Average Precision over top-k, normalised by total relevant items.
    gt_set_for_map = set(gt)
    num_relevant = 0
    ap_sum = 0.0
    for idx, cid in enumerate(pred, start=1):
        if cid in gt_set_for_map:
            num_relevant += 1
            ap_sum += num_relevant / idx          # precision at this rank
    map_k = ap_sum / max(len(gt), 1)

    return {"hit": hit, "recall": recall, "precision": precision, "mrr": mrr, "ndcg": ndcg, "map": map_k}


def save_history_row(
    session_id: int | None,
    method_name: str | None,
    query_id: str | None,
    query: str,
    dense_results: list[dict[str, Any]],
    sparse_results: list[dict[str, Any]],
    hybrid_results: list[dict[str, Any]],
    ground_truth_ranked: list[str],
    dense_metrics: dict[str, float | None],
    sparse_metrics: dict[str, float | None],
    hybrid_metrics: dict[str, float | None],
    timings: dict[str, float],
    method_order: list[str],
) -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO history (
                session_id, method_order, method_name, query_id, query, dense_results, sparse_results, hybrid_results, ground_truth,
                dense_hit, sparse_hit, hybrid_hit,
                dense_recall, sparse_recall, hybrid_recall,
                dense_precision, sparse_precision, hybrid_precision,
                dense_mrr, sparse_mrr, hybrid_mrr,
                dense_time, sparse_time, hybrid_time, total_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                json.dumps(method_order),
                method_name,
                query_id,
                query,
                json.dumps(dense_results, ensure_ascii=False),
                json.dumps(sparse_results, ensure_ascii=False),
                json.dumps(hybrid_results, ensure_ascii=False),
                json.dumps(ground_truth_ranked, ensure_ascii=False),
                dense_metrics["hit"],
                sparse_metrics["hit"],
                hybrid_metrics["hit"],
                dense_metrics["recall"],
                sparse_metrics["recall"],
                hybrid_metrics["recall"],
                dense_metrics["precision"],
                sparse_metrics["precision"],
                hybrid_metrics["precision"],
                dense_metrics["mrr"],
                sparse_metrics["mrr"],
                hybrid_metrics["mrr"],
                float(timings.get("dense_time", 0.0)),
                float(timings.get("sparse_time", 0.0)),
                float(timings.get("hybrid_time", 0.0)),
                float(timings.get("total_time", 0.0)),
            ),
        )
        conn.commit()


def _safe_json_list(value: str | None) -> list:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def _safe_json_dict(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def get_history_rows(limit: int = HISTORY_LIMIT, session_id: int | None = None) -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        if session_id is None:
            rows = conn.execute(
                """
                SELECT
                    id, session_id, method_order, method_name, query_id, query, dense_results, sparse_results, hybrid_results, ground_truth,
                    dense_hit, sparse_hit, hybrid_hit,
                    dense_recall, sparse_recall, hybrid_recall,
                    dense_precision, sparse_precision, hybrid_precision,
                    dense_mrr, sparse_mrr, hybrid_mrr,
                    dense_time, sparse_time, hybrid_time, total_time,
                    timestamp
                FROM history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT
                    id, session_id, method_order, method_name, query_id, query, dense_results, sparse_results, hybrid_results, ground_truth,
                    dense_hit, sparse_hit, hybrid_hit,
                    dense_recall, sparse_recall, hybrid_recall,
                    dense_precision, sparse_precision, hybrid_precision,
                    dense_mrr, sparse_mrr, hybrid_mrr,
                    dense_time, sparse_time, hybrid_time, total_time,
                    timestamp
                FROM history
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["dense_results"] = _safe_json_list(item.get("dense_results"))
        item["sparse_results"] = _safe_json_list(item.get("sparse_results"))
        item["hybrid_results"] = _safe_json_list(item.get("hybrid_results"))
        item["ground_truth"] = _safe_json_list(item.get("ground_truth"))
        item["method_order"] = _safe_json_list(item.get("method_order"))
        out.append(item)
    return out


def save_history_row_v3(
    session_id: int | None,
    query_id: str | None,
    query: str,
    hybrid_results: list[dict[str, Any]],
    reranked_results: list[dict[str, Any]],
    ground_truth_ranked: list[str],
    hybrid_metrics: dict[str, float | None],
    reranking_metrics: dict[str, float | None],
    timings: dict[str, float],
    params: dict[str, Any] | None = None,
) -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO history_v3 (
                session_id, query_id, query, hybrid_results, reranked_results, ground_truth,
                hybrid_hit, hybrid_recall, hybrid_precision, hybrid_mrr, hybrid_ndcg, hybrid_map,
                reranking_hit, reranking_recall, reranking_precision, reranking_mrr, reranking_ndcg, reranking_map,
                retrieval_time, reranking_time, total_time, params
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                query_id,
                query,
                json.dumps(hybrid_results, ensure_ascii=False),
                json.dumps(reranked_results, ensure_ascii=False),
                json.dumps(ground_truth_ranked, ensure_ascii=False),
                hybrid_metrics.get("hit"),
                hybrid_metrics.get("recall"),
                hybrid_metrics.get("precision"),
                hybrid_metrics.get("mrr"),
                hybrid_metrics.get("ndcg"),
                hybrid_metrics.get("map"),
                reranking_metrics.get("hit"),
                reranking_metrics.get("recall"),
                reranking_metrics.get("precision"),
                reranking_metrics.get("mrr"),
                reranking_metrics.get("ndcg"),
                reranking_metrics.get("map"),
                float(timings.get("retrieval_time", 0.0)),
                float(timings.get("reranking_time", 0.0)),
                float(timings.get("total_time", 0.0)),
                json.dumps(params, ensure_ascii=False) if params else None,
            ),
        )
        conn.commit()


def get_history_rows_v3(limit: int = HISTORY_LIMIT, session_id: int | None = None) -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        if session_id is None:
            rows = conn.execute(
                """
                SELECT
                    id, session_id, query_id, query, hybrid_results, reranked_results,
                    ground_truth, hybrid_hit, hybrid_recall, hybrid_precision, hybrid_mrr, hybrid_ndcg, hybrid_map,
                    reranking_hit, reranking_recall, reranking_precision, reranking_mrr, reranking_ndcg, reranking_map,
                    retrieval_time, reranking_time, total_time, timestamp, params
                FROM history_v3
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT
                    id, session_id, query_id, query, hybrid_results, reranked_results,
                    ground_truth, hybrid_hit, hybrid_recall, hybrid_precision, hybrid_mrr, hybrid_ndcg, hybrid_map,
                    reranking_hit, reranking_recall, reranking_precision, reranking_mrr, reranking_ndcg, reranking_map,
                    retrieval_time, reranking_time, total_time, timestamp, params
                FROM history_v3
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["hybrid_results"] = _safe_json_list(item.get("hybrid_results"))
        item["reranked_results"] = _safe_json_list(item.get("reranked_results"))
        item["ground_truth"] = _safe_json_list(item.get("ground_truth"))
        item["params"] = _safe_json_dict(item.get("params"))
        out.append(item)
    return out


def summarize_from_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    metrics = {
        "dense": {"hit_total": 0.0, "recall_total": 0.0, "precision_total": 0.0, "mrr_total": 0.0, "time_total": 0.0, "count": 0.0},
        "sparse": {"hit_total": 0.0, "recall_total": 0.0, "precision_total": 0.0, "mrr_total": 0.0, "time_total": 0.0, "count": 0.0},
        "hybrid": {"hit_total": 0.0, "recall_total": 0.0, "precision_total": 0.0, "mrr_total": 0.0, "time_total": 0.0, "count": 0.0},
    }

    for r in rows:
        for name in ("dense", "sparse", "hybrid"):
            hit = r.get(f"{name}_hit")
            recall = r.get(f"{name}_recall")
            precision = r.get(f"{name}_precision")
            mrr = r.get(f"{name}_mrr")
            tval = r.get(f"{name}_time")
            if hit is None or recall is None or precision is None or mrr is None:
                continue

            metrics[name]["hit_total"] += float(hit)
            metrics[name]["recall_total"] += float(recall)
            metrics[name]["precision_total"] += float(precision)
            metrics[name]["mrr_total"] += float(mrr)
            metrics[name]["time_total"] += float(tval or 0.0)
            metrics[name]["count"] += 1.0

    summary: dict[str, dict[str, float]] = {}
    for name, stat in metrics.items():
        c = stat["count"]
        if c <= 0:
            summary[name] = {"hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "avg_time": 0.0}
        else:
            summary[name] = {
                "hit": stat["hit_total"] / c,
                "recall": stat["recall_total"] / c,
                "precision": stat["precision_total"] / c,
                "mrr": stat["mrr_total"] / c,
                "avg_time": stat["time_total"] / c,
            }
    return summary


def summarize_from_rows_v3(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    retrieval_total = 0.0
    reranking_total = 0.0
    total_total = 0.0
    count = 0.0
    hybrid_hit_total = 0.0
    hybrid_recall_total = 0.0
    hybrid_precision_total = 0.0
    hybrid_mrr_total = 0.0
    hybrid_ndcg_total = 0.0
    hybrid_map_total = 0.0
    hybrid_metric_count = 0.0
    rerank_hit_total = 0.0
    rerank_recall_total = 0.0
    rerank_precision_total = 0.0
    rerank_mrr_total = 0.0
    rerank_ndcg_total = 0.0
    rerank_map_total = 0.0
    rerank_metric_count = 0.0
    for row in rows:
        retrieval_total += float(row.get("retrieval_time", 0.0) or 0.0)
        reranking_total += float(row.get("reranking_time", 0.0) or 0.0)
        total_total += float(row.get("total_time", 0.0) or 0.0)
        count += 1.0
        if (
            row.get("hybrid_hit") is not None
            and row.get("hybrid_recall") is not None
            and row.get("hybrid_precision") is not None
            and row.get("hybrid_mrr") is not None
            and row.get("hybrid_ndcg") is not None
            and row.get("hybrid_map") is not None
        ):
            hybrid_hit_total += float(row["hybrid_hit"])
            hybrid_recall_total += float(row["hybrid_recall"])
            hybrid_precision_total += float(row["hybrid_precision"])
            hybrid_mrr_total += float(row["hybrid_mrr"])
            hybrid_ndcg_total += float(row["hybrid_ndcg"])
            hybrid_map_total += float(row["hybrid_map"])
            hybrid_metric_count += 1.0
        if (
            row.get("reranking_hit") is not None
            and row.get("reranking_recall") is not None
            and row.get("reranking_precision") is not None
            and row.get("reranking_mrr") is not None
            and row.get("reranking_ndcg") is not None
            and row.get("reranking_map") is not None
        ):
            rerank_hit_total += float(row["reranking_hit"])
            rerank_recall_total += float(row["reranking_recall"])
            rerank_precision_total += float(row["reranking_precision"])
            rerank_mrr_total += float(row["reranking_mrr"])
            rerank_ndcg_total += float(row["reranking_ndcg"])
            rerank_map_total += float(row["reranking_map"])
            rerank_metric_count += 1.0

    if count <= 0:
        return {
            "hybrid": {"hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "ndcg": 0.0, "map": 0.0},
            "minilm": {"hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "ndcg": 0.0, "map": 0.0},
            "reranking": {"hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "ndcg": 0.0, "map": 0.0},
            "timings": {"avg_retrieval_time": 0.0, "avg_reranking_time": 0.0, "avg_total_time": 0.0},
        }
    return {
        "hybrid": {
            "hit": (hybrid_hit_total / hybrid_metric_count) if hybrid_metric_count > 0 else 0.0,
            "recall": (hybrid_recall_total / hybrid_metric_count) if hybrid_metric_count > 0 else 0.0,
            "precision": (hybrid_precision_total / hybrid_metric_count) if hybrid_metric_count > 0 else 0.0,
            "mrr": (hybrid_mrr_total / hybrid_metric_count) if hybrid_metric_count > 0 else 0.0,
            "ndcg": (hybrid_ndcg_total / hybrid_metric_count) if hybrid_metric_count > 0 else 0.0,
            "map": (hybrid_map_total / hybrid_metric_count) if hybrid_metric_count > 0 else 0.0,
        },
        "minilm": {"hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "ndcg": 0.0, "map": 0.0},
        "reranking": {
            "hit": (rerank_hit_total / rerank_metric_count) if rerank_metric_count > 0 else 0.0,
            "recall": (rerank_recall_total / rerank_metric_count) if rerank_metric_count > 0 else 0.0,
            "precision": (rerank_precision_total / rerank_metric_count) if rerank_metric_count > 0 else 0.0,
            "mrr": (rerank_mrr_total / rerank_metric_count) if rerank_metric_count > 0 else 0.0,
            "ndcg": (rerank_ndcg_total / rerank_metric_count) if rerank_metric_count > 0 else 0.0,
            "map": (rerank_map_total / rerank_metric_count) if rerank_metric_count > 0 else 0.0,
        },
        "timings": {
            "avg_retrieval_time": retrieval_total / count,
            "avg_reranking_time": reranking_total / count,
            "avg_total_time": total_total / count,
        },
    }


def aggregate_v3_by_query(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, float | str]] = {}
    for row in rows:
        query = str(row.get("query", "")).strip()
        if not query:
            continue
        if query not in grouped:
            grouped[query] = {
                "original_query": query,
                "retrieval_total": 0.0,
                "reranking_total": 0.0,
                "total_total": 0.0,
                "count": 0.0,
            }
        grouped[query]["retrieval_total"] = float(grouped[query]["retrieval_total"]) + float(row.get("retrieval_time", 0.0) or 0.0)
        grouped[query]["reranking_total"] = float(grouped[query]["reranking_total"]) + float(row.get("reranking_time", 0.0) or 0.0)
        grouped[query]["total_total"] = float(grouped[query]["total_total"]) + float(row.get("total_time", 0.0) or 0.0)
        grouped[query]["count"] = float(grouped[query]["count"]) + 1.0

    aggregated: list[dict[str, Any]] = []
    for item in grouped.values():
        count = max(float(item["count"]), 1.0)
        aggregated.append(
            {
                "original_query": str(item["original_query"]),
                "avg_retrieval_time": float(item["retrieval_total"]) / count,
                "avg_reranking_time": float(item["reranking_total"]) / count,
                "avg_total_time": float(item["total_total"]) / count,
            }
        )
    aggregated.sort(key=lambda x: x["avg_total_time"], reverse=True)
    return aggregated


def format_duration(seconds: float | None) -> str:
    value = float(seconds or 0.0)
    if value < 0.001:
        return f"{value * 1_000_000:.0f}µs"
    if value < 1.0:
        return f"{value * 1000:.3f}ms"
    return f"{value:.3f}s"


def best_method_by_mrr(summary: dict[str, dict[str, float]]) -> str:
    return max(summary, key=lambda name: summary[name]["mrr"])


def _view_for_method(results: list[dict[str, Any]], ground_truth_ranked: list[str]) -> list[dict[str, Any]]:
    gt = set(ground_truth_ranked)
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(results[:TOP_K]):
        cid = item.get("control_id", "")
        title = item.get("title", "")
        score = float(item.get("score", 0.0))
        rows.append(
            {
                "control_id": cid,
                "text": f"{cid} - {title} ({score:.3f})",
                "is_match": cid in gt,
                "is_top1": idx == 0,
            }
        )
    return rows


def _view_for_v3_reranking(results: list[dict[str, Any]], ground_truth_ranked: list[str]) -> list[dict[str, Any]]:
    gt = set(ground_truth_ranked)
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(results[:TOP_K]):
        cid = str(item.get("control_id", "")).strip()
        title = str(item.get("title", "")).strip()
        combined = float(item.get("combined_score", 0.0) or 0.0)
        rerank = float(item.get("rerank_score", item.get("score", 0.0)) or 0.0)
        rows.append(
            {
                "control_id": cid,
                "text": f"{cid} - {title} (combined={combined:.3f}, ce={rerank:.3f})",
                "is_match": cid in gt,
                "is_top1": idx == 0,
            }
        )
    return rows


def _view_for_v3_hybrid(results: list[dict[str, Any]], ground_truth_ranked: list[str]) -> list[dict[str, Any]]:
    gt = set(ground_truth_ranked)
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(results[:TOP_K]):
        cid = str(item.get("control_id", "")).strip()
        title = str(item.get("title", "")).strip()
        score = float(item.get("hybrid_score", item.get("score", 0.0)) or 0.0)
        rows.append(
            {
                "control_id": cid,
                "text": f"{cid} - {title} ({score:.3f})",
                "is_match": cid in gt,
                "is_top1": idx == 0,
            }
        )
    return rows


def _format_method_accuracy_for_v3(row: dict[str, Any], prefix: str, label: str, k: int = TOP_K) -> str:
    hit = row.get(f"{prefix}_hit")
    recall = row.get(f"{prefix}_recall")
    precision = row.get(f"{prefix}_precision")
    mrr = row.get(f"{prefix}_mrr")
    ndcg = row.get(f"{prefix}_ndcg")
    map_val = row.get(f"{prefix}_map")
    if hit is None or recall is None or precision is None or mrr is None or ndcg is None or map_val is None:
        return f"{label}: N/A"
    return (
        f"{label} → Hit@{k}: {float(hit):.2f} | "
        f"Recall@{k}: {float(recall):.2f} | "
        f"Precision@{k}: {float(precision):.2f} | "
        f"MRR: {float(mrr):.3f} | "
        f"NDCG@{k}: {float(ndcg):.3f} | "
        f"MAP@{k}: {float(map_val):.3f}"
    )


def _format_accuracy_for_v3(row: dict[str, Any], k: int = TOP_K) -> str:
    hybrid_line = _format_method_accuracy_for_v3(row, "hybrid", "Hybrid", k=k)
    reranking_line = _format_method_accuracy_for_v3(row, "reranking", "BGE", k=k)
    if hybrid_line.endswith("N/A") and reranking_line.endswith("N/A"):
        return "N/A (ground truth unavailable)"
    return f"{hybrid_line}\n{reranking_line}"


def _empty_metrics() -> dict[str, float | None]:
    return {"hit": None, "recall": None, "precision": None, "mrr": None, "ndcg": None, "map": None}


def _process_retrieval_only(
    query_id: str | None,
    query: str,
    ground_truth_ranked: list[str],
    k: int = TOP_K,
    method_order: list[str] | None = None,
    session_id: int | None = None,
    single_method: bool = False,
) -> dict[str, Any]:
    expected_count = 1 if single_method else None
    order = normalize_method_order(method_order, expected_count=expected_count)
    if single_method and len(order) != 1:
        raise Exception("Single-method evaluation expected exactly one method.")
    retrieval = pipeline.retriever.retrieve(query=query, k=k, method_order=order)
    active_methods = set(order)
    executed_method = order[0] if len(order) == 1 else None

    dense_top = compact_results(retrieval.get("dense_results", []), "dense_score", k=k) if "dense" in active_methods else []
    sparse_top = compact_results(retrieval.get("sparse_results", []), "sparse_score", k=k) if "sparse" in active_methods else []
    hybrid_top = compact_results(retrieval.get("hybrid_results", []), "hybrid_score", k=k) if "hybrid" in active_methods else []

    dense_ids = [x["control_id"] for x in dense_top]
    sparse_ids = [x["control_id"] for x in sparse_top]
    hybrid_ids = [x["control_id"] for x in hybrid_top]

    dense_metrics = compute_metrics(dense_ids, ground_truth_ranked, k=k) if "dense" in active_methods else _empty_metrics()
    sparse_metrics = compute_metrics(sparse_ids, ground_truth_ranked, k=k) if "sparse" in active_methods else _empty_metrics()
    hybrid_metrics = compute_metrics(hybrid_ids, ground_truth_ranked, k=k) if "hybrid" in active_methods else _empty_metrics()
    timings = retrieval.get("timings", {"dense_time": 0.0, "sparse_time": 0.0, "hybrid_time": 0.0, "total_time": 0.0})

    save_history_row(
        session_id=session_id,
        method_name=executed_method,
        query_id=query_id,
        query=query,
        dense_results=dense_top,
        sparse_results=sparse_top,
        hybrid_results=hybrid_top,
        ground_truth_ranked=ground_truth_ranked,
        dense_metrics=dense_metrics,
        sparse_metrics=sparse_metrics,
        hybrid_metrics=hybrid_metrics,
        timings=timings,
        method_order=order,
    )

    return {
        "query_id": query_id,
        "query": query,
        "ground_truth_ranked": ground_truth_ranked,
        "dense_results": dense_top,
        "sparse_results": sparse_top,
        "hybrid_results": hybrid_top,
        "metrics": {
            "dense": dense_metrics,
            "sparse": sparse_metrics,
            "hybrid": hybrid_metrics,
        },
        "timings": timings,
        "method_order": order,
        "method_name": executed_method,
        "session_id": session_id,
    }


def _run_bulk_in_background(payload: list[dict[str, Any]], method_order: list[str], session_id: int, single_method: bool) -> None:
    global BULK_THREAD
    try:
        total = len(payload)
        reset_progress(total, session_id=session_id, method_order=method_order)
        processed_rows: list[dict[str, Any]] = []

        for idx, item in enumerate(payload, start=1):
            if not isinstance(item, dict):
                set_progress(idx - 1, total, "invalid item format", False, "Each item must be an object")
                return

            query_id = item.get("query_id")
            query_text = str(item.get("query", "")).strip()
            gt_ranked = item.get("ground_truth_ranked")
            if gt_ranked is None:
                gt_ranked = item.get("ground_truth", [])

            if not query_text:
                set_progress(idx - 1, total, "missing query", False, "Each item requires a non-empty 'query'")
                return
            if not isinstance(gt_ranked, list):
                set_progress(idx - 1, total, "invalid ground_truth_ranked", False, "ground_truth_ranked must be a list")
                return

            set_progress(idx - 1, total, f"retrieving query {idx}/{total}", True)

            processed = _process_retrieval_only(
                query_id=query_id,
                query=query_text,
                ground_truth_ranked=gt_ranked,
                k=TOP_K,
                method_order=method_order,
                session_id=session_id,
                single_method=single_method,
            )
            processed_rows.append(processed)

            with PROGRESS_LOCK:
                PROGRESS_STATE["bulk_results"].append(processed)

            set_progress(idx, total, f"processed query {idx}/{total}", True)

        set_progress(total, total, "completed", False)

    except Exception as exc:
        import traceback
        set_progress(PROGRESS_STATE["current"], PROGRESS_STATE["total"], f"error: {exc}", False, str(exc) + "\n" + traceback.format_exc())
    finally:
        BULK_THREAD = None


def _run_bulk_v3_in_background(queries: list[dict[str, Any]], session_id: int, bulk_params: dict[str, Any] | None = None) -> None:
    global V3_BULK_THREAD
    try:
        total = len(queries)
        reset_progress(total, session_id=session_id, method_order=["hybrid", "reranking"])

        for idx, item in enumerate(queries, start=1):
            query_text = str(item.get("query", "")).strip()
            query_id = item.get("query_id")
            gt_ranked = item.get("ground_truth_ranked", [])
            if not isinstance(gt_ranked, list):
                gt_ranked = []
            gt_ranked = [str(x).strip() for x in gt_ranked if str(x).strip()]

            if not query_text:
                set_progress(idx - 1, total, f"skipped empty query {idx}/{total}", True)
                continue

            set_progress(idx - 1, total, f"processing V3 query {idx}/{total}", True)

            try:
                _bp = bulk_params or {}
                result = pipeline_v3.run(query=query_text, k=TOP_K, **_bp)
                hybrid_ids = [s["control_id"] for s in result.get("hybrid_results", [])]
                reranked = result.get("reranked_results", [])
                reranked_ids = [s["control_id"] for s in reranked]

                hybrid_metrics = compute_metrics(
                    predicted_ids=hybrid_ids,
                    ground_truth_ranked=gt_ranked,
                    k=TOP_K,
                )
                reranking_metrics = compute_metrics(
                    predicted_ids=reranked_ids,
                    ground_truth_ranked=gt_ranked,
                    k=TOP_K,
                )

                raw_timings = result.get("timings", {})
                timings = {
                    "retrieval_time": raw_timings.get("retrieval_time", 0.0),
                    "reranking_time": raw_timings.get("reranking_time", 0.0),
                    "total_time": raw_timings.get("total_time", 0.0),
                }

                save_history_row_v3(
                    session_id=session_id,
                    query_id=query_id,
                    query=query_text,
                    hybrid_results=result.get("hybrid_results", []),
                    reranked_results=reranked,
                    ground_truth_ranked=gt_ranked,
                    hybrid_metrics=hybrid_metrics,
                    reranking_metrics=reranking_metrics,
                    timings=timings,
                    params=result.get("params"),
                )
            except Exception as exc:
                import traceback
                print(f"[bulk-v3] Error on query {idx}: {exc}\n{traceback.format_exc()}")

            set_progress(idx, total, f"processed V3 query {idx}/{total}", True)

        set_progress(total, total, "completed", False)

    except Exception as exc:
        import traceback
        set_progress(
            PROGRESS_STATE["current"],
            PROGRESS_STATE["total"],
            f"error: {exc}",
            False,
            str(exc) + "\n" + traceback.format_exc(),
        )
    finally:
        V3_BULK_THREAD = None
        with V3_QUEUE_LOCK:
            has_queue = bool(V3_QUEUE)
        if has_queue:
            V3_BULK_THREAD = threading.Thread(target=_process_v3_queue, daemon=True)
            V3_BULK_THREAD.start()


V3_INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V3 - Hybrid Retrieval + Cross-Encoder Reranking</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; color: #222; }
    textarea { width: 100%; border: 1px solid #ccc; border-radius: 6px; padding: 8px; box-sizing: border-box; }
    #query { height: 80px; margin-bottom: 8px; }
    .actions { display: flex; gap: 8px; margin: 10px 0; flex-wrap: wrap; }
    button, a.btn { padding: 8px 14px; border: 1px solid #bbb; background: #f7f7f7; border-radius: 6px; cursor: pointer; text-decoration: none; color: #222; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .section { margin-top: 16px; }
    .summary { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px; padding: 12px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }
    th { background: #f3f3f3; }
    tr.top-row { background: #eafbe7; }
    tr.data-row { cursor: pointer; }
    .mono { font-family: Consolas, monospace; }
    .small { font-size: 12px; color: #555; }
    #status { margin-top: 6px; font-size: 13px; color: #444; }
    #progressWrap { margin-top: 8px; background: #eee; border-radius: 8px; overflow: hidden; height: 18px; border: 1px solid #ddd; display: none; }
    #progressBar { width: 0%; height: 100%; background: #4caf50; transition: width 0.3s ease; }
    #progressText { margin-top: 6px; font-size: 12px; color: #333; }
    #modalOverlay { display: none; position: fixed; z-index: 20; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.45); }
    #modalBox { background: #fff; width: min(800px, 90%); margin: 6% auto; border-radius: 8px; padding: 16px; border: 1px solid #ddd; }
    #modalClose { float: right; border: 0; background: transparent; font-size: 20px; cursor: pointer; }
    .param-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin: 8px 0; }
    .param-item label { display: block; font-size: 12px; color: #555; margin-bottom: 2px; }
    .param-item input { width: 100%; border: 1px solid #ccc; border-radius: 4px; padding: 5px 8px; font-family: Consolas, monospace; font-size: 13px; box-sizing: border-box; }
    .queue-section { margin-top: 16px; }
    .queue-item { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-top: 10px; background: #fafbfc; }
    .queue-item.active { border-color: #4caf50; background: #f0faf0; }
    .queue-item.done { border-color: #bbb; background: #f5f5f5; opacity: 0.7; }
    .queue-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .queue-header h4 { margin: 0; }
    .queue-remove { background: #fee; color: #c00; border: 1px solid #daa; border-radius: 4px; padding: 2px 10px; cursor: pointer; font-size: 12px; }
    .queue-bulk-input { height: 100px; font-family: Consolas, monospace; font-size: 12px; }
    .queue-params { margin-top: 8px; }
    .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid #4caf50; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 6px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .queue-list { margin-top: 10px; }
    #addQueryPanel { display: none; margin-top: 12px; }
    #addQueryPanel textarea { height: 120px; }
    .file-input-wrap { margin: 8px 0; display: flex; align-items: center; gap: 8px; }
    .file-input-wrap label { font-size: 13px; color: #555; cursor: pointer; padding: 6px 12px; border: 1px solid #bbb; border-radius: 6px; background: #f7f7f7; }
    .file-input-wrap input[type="file"] { display: none; }
    .file-input-wrap .file-name { font-size: 12px; color: #888; }
  </style>
</head>
<body>
  <h2>RAG V3 - Hybrid Retrieval + Cross-Encoder Reranking</h2>

  <div class="section">
    <h3>Single Query (V3 Pipeline)</h3>
    <textarea id="query" placeholder="Masukkan query..."></textarea>
    <textarea id="gtSingle" placeholder='Ground truth ranked (JSON array), contoh: ["A.5.11"]'></textarea>
    <div class="summary" style="padding:10px;">
      <h4 style="margin:0 0 6px 0;">Pipeline Parameters</h4>
      <div class="param-grid">
        <div class="param-item">
          <label>alpha_dense (default 0.6)</label>
          <input type="number" id="alpha_dense" value="0.6" step="0.01" min="0" max="1" />
        </div>
        <div class="param-item">
          <label>alpha_sparse (default 0.4)</label>
          <input type="number" id="alpha_sparse" value="0.4" step="0.01" min="0" max="1" />
        </div>
        <div class="param-item">
          <label>candidate_pool (default 10)</label>
          <input type="number" id="candidate_pool" value="10" step="1" min="1" max="50" />
        </div>
        <div class="param-item">
          <label>alpha_ce (default 0.8)</label>
          <input type="number" id="alpha_ce" value="0.8" step="0.01" min="0" max="1" />
        </div>
        <div class="param-item">
          <label>alpha_hybrid (default 0.2)</label>
          <input type="number" id="alpha_hybrid" value="0.2" step="0.01" min="0" max="1" />
        </div>
      </div>
    </div>
    <div class="actions">
      <button onclick="runV3()">Run V3 Query</button>
      <a class="btn" href="/history/v3" target="_blank">Open V3 History</a>
      <a class="btn" href="/">Back to V1 Dashboard</a>
    </div>
    <div id="status"></div>
  </div>

  <div class="section">
    <h3>Bulk Input (V3 Pipeline)</h3>
    <textarea id="bulkInput" placeholder='[{"query_id":"Q1","query":"...","ground_truth_ranked":["A.5.18","A.5.16","A.5.15"]}]'></textarea>
    <div style="margin: 10px 0; padding: 10px; background: #f0f7ff; border-radius: 6px;">
      <div style="margin-bottom: 8px; font-weight: bold;">Session Mode:</div>
      <div style="display: flex; gap: 10px; align-items: center;">
        <button id="newSessionBtn" onclick="setSessionMode('new')" style="background: #e3f2e3; border-color: #4caf50;">Start New Session</button>
        <button id="continueSessionBtn" onclick="setSessionMode('continue')" style="background: #f5f5f5;">Continue Session</button>
        <span id="sessionInfo" class="small" style="margin-left: 10px;">Loading session info...</span>
      </div>
    </div>
    <div class="actions">
      <button id="bulkBtnV3" onclick="runBulkV3()">Run Bulk V3 Evaluation</button>
      <button id="addQueueBtn" onclick="addToQueue()">Add to Queue</button>
    </div>
    <div id="progressWrap"><div id="progressBar"></div></div>
    <div id="progressText" class="small"></div>
    <div id="bulkResults"></div>
  </div>

  <div class="queue-section">
    <h3>Queue <button onclick="clearQueue()" style="font-size:12px;padding:4px 10px;">Clear All</button></h3>
    <button id="addQueryToggle" onclick="toggleAddQueryPanel()" style="margin-bottom:8px;">Add Query</button>
    <div id="addQueryPanel" style="display:none;">
      <div class="file-input-wrap">
        <label for="jsonFileInput">Load JSON File</label>
        <input type="file" id="jsonFileInput" accept=".json" onchange="loadJsonFile(event)" />
        <span id="fileName" class="file-name">No file selected</span>
      </div>
      <textarea id="addQueryInput" placeholder='Paste JSON array here or load a file above:\n[{"query_id":"Q1","query":"...","ground_truth_ranked":["A.5.18"]}]'></textarea>
      <div class="summary" style="padding:10px;margin:8px 0;">
        <h4 style="margin:0 0 6px 0;">Session</h4>
        <div class="actions" style="margin:0;">
          <button id="aqSessionNew" onclick="setAqSessionMode('new')" style="background:#4caf50;color:#fff;border-color:#4caf50;">New Session</button>
          <button id="aqSessionContinue" onclick="setAqSessionMode('continue')">Continue Last</button>
        </div>
        <input type="hidden" id="aqSessionMode" value="new" />
      </div>
      <div class="summary" style="padding:10px;margin:8px 0;">
        <h4 style="margin:0 0 6px 0;">Pipeline Parameters</h4>
        <div class="param-grid">
          <div class="param-item">
            <label>alpha_dense (default 0.6)</label>
            <input type="number" id="aq_alpha_dense" value="0.6" step="0.01" min="0" max="1" />
          </div>
          <div class="param-item">
            <label>alpha_sparse (default 0.4)</label>
            <input type="number" id="aq_alpha_sparse" value="0.4" step="0.01" min="0" max="1" />
          </div>
          <div class="param-item">
            <label>candidate_pool (default 10)</label>
            <input type="number" id="aq_candidate_pool" value="10" step="1" min="1" />
          </div>
          <div class="param-item">
            <label>alpha_ce (default 0.8)</label>
            <input type="number" id="aq_alpha_ce" value="0.8" step="0.01" min="0" max="1" />
          </div>
        </div>
      </div>
      <div class="actions">
        <button onclick="submitAddQuery()">Submit to Queue</button>
        <button onclick="toggleAddQueryPanel()">Cancel</button>
      </div>
    </div>
    <div id="queueList" class="queue-list"></div>
    <div id="queueEmpty" class="small" style="color:#999;">No items in queue.</div>
  </div>

  <div class="section">
    <h3>Top Reranked Result</h3>
    <div id="topControl" class="summary">-</div>
  </div>

  <div class="section">
    <h3>LLM Answer</h3>
    <pre id="answerBox" class="summary" style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">-</pre>
  </div>

  <div class="section">
    <h3>Reranked Results (Cross-Encoder)</h3>
    <div id="rerankedTable"></div>
  </div>

  <div class="section">
    <h3>Hybrid Results (Before Reranking)</h3>
    <div id="hybridTable"></div>
  </div>

  <div class="section">
    <h3>Timing Breakdown</h3>
    <div id="timingBox" class="summary">-</div>
  </div>

  <div id="modalOverlay">
    <div id="modalBox">
      <button id="modalClose" onclick="closeModal()">&times;</button>
      <h3 id="modalTitle"></h3>
      <p><strong>Objective:</strong> <span id="modalObjective"></span></p>
      <p><strong>Description:</strong> <span id="modalDescription"></span></p>
    </div>
  </div>

  <script>
    let currentSessionId = null;
    let nextSessionId = null;

    async function loadSessionInfo() {
      try {
        const res = await fetch('/session-info');
        const data = await res.json();
        currentSessionId = data.latest_session_id;
        nextSessionId = currentSessionId ? currentSessionId + 1 : 1;
        updateSessionInfoDisplay();
      } catch(e) {
        console.error('Failed to load session info:', e);
      }
    }

    function updateSessionInfoDisplay() {
      const mode = document.querySelector('input[name="sessionMode"]:checked').value;
      const infoDiv = document.getElementById('sessionInfoDisplay');
      
      if (mode === 'new') {
        infoDiv.textContent = `Will create new session ID: ${nextSessionId}`;
      } else {
        infoDiv.textContent = `Will continue session ID: ${currentSessionId ? currentSessionId : 'No active session (will create new)'}`;
      }
    }

    // Auto-sync: alpha_ce + alpha_hybrid = 1
    document.getElementById('alpha_ce').addEventListener('input', function() {
      const v = parseFloat(this.value);
      if (!isNaN(v)) document.getElementById('alpha_hybrid').value = (1 - v).toFixed(2);
    });
    document.getElementById('alpha_hybrid').addEventListener('input', function() {
      const v = parseFloat(this.value);
      if (!isNaN(v)) document.getElementById('alpha_ce').value = (1 - v).toFixed(2);
    });

    let v3PollInterval = null;
    let queueData = [];

    function saveQueueUIState() {
      try {
        localStorage.setItem('v3_queue_ui', JSON.stringify(queueData));
      } catch(e) {}
    }
    function loadQueueUIState() {
      try {
        const saved = localStorage.getItem('v3_queue_ui');
        if (saved) queueData = JSON.parse(saved);
      } catch(e) {}
    }

    function fmtScore(n) {
      if (n < 1) return n.toFixed(4);
      return n.toFixed(3);
    }
    function openModal(item) {
      document.getElementById('modalTitle').textContent = `${item.control_id} - ${item.title}`;
      document.getElementById('modalObjective').textContent = item.objective || '-';
      document.getElementById('modalDescription').textContent = item.description || '-';
      document.getElementById('modalOverlay').style.display = 'block';
    }
    function closeModal() { document.getElementById('modalOverlay').style.display = 'none'; }

    document.addEventListener('DOMContentLoaded', function() {
      updateSessionInfoDisplay();
      document.querySelectorAll('input[name="sessionMode"]').forEach(radio => {
        radio.addEventListener('change', updateSessionInfoDisplay);
      });
    });

    function renderTable(targetId, rows, scoreKey = 'score') {
      const target = document.getElementById(targetId);
      if (!rows || rows.length === 0) { target.innerHTML = '<div class="small">No results.</div>'; return; }
      let html = '<table><tr><th>#</th><th>Control ID</th><th>Title</th><th>Score</th></tr>';
      rows.forEach((r, i) => {
        const cls = i === 0 ? ' class="top-row data-row"' : ' class="data-row"';
        html += `<tr${cls} onclick='openModal(${JSON.stringify(r)})'><td>${i+1}</td><td class="mono">${r.control_id}</td><td>${r.title || r.control_id}</td><td class="mono">${fmtScore(r[scoreKey])}</td></tr>`;
      });
      html += '</table>';
      target.innerHTML = html;
    }

    function renderBulkV3Results(results) {
      const target = document.getElementById('bulkResults');
      if (!results || results.length === 0) { target.innerHTML = ''; return; }
      let html = '<table><tr><th>Query ID</th><th>Hybrid Hit</th><th>Reranking Hit</th><th>Hybrid Recall</th><th>Reranking Recall</th><th>Hybrid MRR</th><th>Reranking MRR</th></tr>';
      results.forEach(r => {
        const hy = r.hybrid_metrics || {};
        const re = r.reranking_metrics || {};
        html += `<tr><td class="mono">${r.query_id || '-'}</td><td>${hy.hit_rate ?? '-'}</td><td>${re.hit_rate ?? '-'}</td><td>${fmtScore(hy.recall ?? 0)}</td><td>${fmtScore(re.recall ?? 0)}</td><td>${fmtScore(hy.mrr ?? 0)}</td><td>${fmtScore(re.mrr ?? 0)}</td></tr>`;
      });
      html += '</table>';
      target.innerHTML = html;
    }

    async function updateSessionInfoDisplay() {
      try {
        const res = await fetch('/session-info');
        const data = await res.json();
        const latest = data.latest_session_id ?? 0;
        const nextId = latest + 1;
        const sessionInfo = document.getElementById('sessionInfo');
        const mode = document.querySelector('input[name="sessionMode"]:checked').value;
        if (mode === 'new') {
          sessionInfo.textContent = `New Session ID: ${nextId}`;
        } else {
          sessionInfo.textContent = `Continue Session ID: ${latest}`;
        }
      } catch (e) {
        console.error('Failed to fetch session info:', e);
      }
    }

    async function runV3() {
      const status = document.getElementById('status');
      const query = document.getElementById('query').value.trim();
      if (!query) { status.textContent = 'Query wajib diisi.'; return; }

      status.textContent = 'Processing V3 query...';
      const payload = { query };
      const gt = document.getElementById('gtSingle').value.trim();
      if (gt) { try { payload.ground_truth_ranked = JSON.parse(gt); } catch(e) {} }
      payload.alpha_dense = parseFloat(document.getElementById('alpha_dense').value);
      payload.alpha_sparse = parseFloat(document.getElementById('alpha_sparse').value);
      payload.candidate_pool = parseInt(document.getElementById('candidate_pool').value);
      payload.alpha_ce = parseFloat(document.getElementById('alpha_ce').value);
      try {
        const res = await fetch('/v3', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) { status.textContent = 'Error: ' + (data.error || 'Unknown'); return; }
        
        const top = (data.reranked_results && data.reranked_results[0]) || null;
        document.getElementById('topControl').innerHTML = top
          ? `<strong>${top.control_id}</strong> - ${top.title}<br><span class="small">Score: ${fmtScore(top.score)}</span>`
          : '-';
        document.getElementById('answerBox').textContent = data.answer || '-';
        renderTable('rerankedTable', data.reranked_results, 'reranking_score');
        renderTable('hybridTable', data.hybrid_results);

        const t = data.timings || {};
        document.getElementById('timingBox').innerHTML =
          `Retrieval: ${((t.retrieval_time||0)*1000).toFixed(1)}ms | Reranking: ${((t.reranking_time||0)*1000).toFixed(1)}ms | Total: ${((t.total_time||0)*1000).toFixed(1)}ms`;
        status.textContent = `Done. Session ${data.session_id || '-'}.`;
      } catch (e) {
        status.textContent = 'Error: ' + e.message;
      }
    }

    async function pollV3Progress() {
      try {
        const res = await fetch('/progress');
        const p = await res.json();
        document.getElementById('progressBar').style.width = `${p.percentage}%`;

        let queueInfo = '';
        if (p.queue_label) {
          queueInfo = ` [${p.queue_label} - Queue ${p.queue_index}/${p.queue_total}]`;
        }
        const sid = p.session_id == null ? '-' : p.session_id;
        document.getElementById('progressText').textContent = `Session ${sid} | Processing Query ${p.current} / ${p.total}... (${p.percentage}%) - ${p.status}${queueInfo}`;

        if (p.running) {
          document.getElementById('progressWrap').style.display = 'block';
          document.getElementById('progressText').innerHTML = '<span class="spinner"></span>' + document.getElementById('progressText').textContent;
          document.getElementById('bulkBtnV3').disabled = true;
        }

        if (p.bulk_results && p.bulk_results.length > 0) {
          renderBulkV3Results(p.bulk_results);
        }

        if (p.error) {
          document.getElementById('status').textContent = 'Error: ' + p.error;
          clearInterval(v3PollInterval);
          document.getElementById('bulkBtnV3').disabled = false;
          return;
        }
        if (!p.running && p.current > 0) {
          const sidDone = p.session_id == null ? 'N/A' : p.session_id;
          document.getElementById('status').textContent = `Session ${sidDone} completed. Processed: ${p.current} queries.`;
          document.getElementById('bulkBtnV3').disabled = false;
          updateSessionInfoDisplay();
          refreshQueueList().then(() => {
            if (queueData && queueData.length > 0) return;
            setTimeout(() => {
              fetch('/progress').then(r => r.json()).then(pp => {
                if (pp.running) return;
                clearInterval(v3PollInterval);
                v3PollInterval = null;
              }).catch(() => {
                clearInterval(v3PollInterval);
                v3PollInterval = null;
              });
            }, 1000);
          });
        }
      } catch (e) {
        console.error('V3 poll error:', e);
      }
    }

    async function runBulkV3() {
      const status = document.getElementById('status');
      const progressWrap = document.getElementById('progressWrap');
      const progressBar = document.getElementById('progressBar');
      const progressText = document.getElementById('progressText');
      const bulkResults = document.getElementById('bulkResults');
      const raw = document.getElementById('bulkInput').value.trim();
      
      if (!raw) { status.textContent = 'Bulk input wajib diisi.'; return; }
      
      let payload = null;
      let cleanRaw = raw.replace(/,\s*([\]}])/g, '$1');
      try { payload = JSON.parse(cleanRaw); } catch(e) {
        try { payload = JSON.parse('[' + cleanRaw + ']'); } catch(e2) {
          status.textContent = 'JSON bulk tidak valid.'; return;
        }
      }
      if (!Array.isArray(payload)) payload = [payload];
      
      const sessionMode = document.querySelector('input[name="sessionMode"]:checked').value;
      
      status.textContent = 'Starting bulk V3 evaluation...';
      document.getElementById('bulkBtnV3').disabled = true;
      bulkResults.innerHTML = '';
      progressWrap.style.display = 'block';
      progressBar.style.width = '0%';
      progressText.textContent = 'Preparing...';
      
      try {
        const res = await fetch('/bulk-v3', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({
            queries: payload,
            session_mode: sessionMode,
            alpha_dense: parseFloat(document.getElementById('alpha_dense').value),
            alpha_sparse: parseFloat(document.getElementById('alpha_sparse').value),
            candidate_pool: parseInt(document.getElementById('candidate_pool').value),
            alpha_ce: parseFloat(document.getElementById('alpha_ce').value),
          })
        });
        
        const data = await res.json();
        if (!res.ok) { 
          status.textContent = 'Error: ' + (data.error || 'Unknown'); 
          progressWrap.style.display = 'none';
          document.getElementById('bulkBtnV3').disabled = false;
          return; 
        }
        
        const sid = data.session_id == null ? '-' : data.session_id;
        status.textContent = `Bulk V3 started. Session ${sid}.`;
        v3PollInterval = setInterval(pollV3Progress, 500);
        
      } catch (e) {
        status.textContent = 'Error: ' + e.message;
        progressWrap.style.display = 'none';
        document.getElementById('bulkBtnV3').disabled = false;
      }
    }

    async function addToQueue() {
      const raw = document.getElementById('bulkInput').value.trim();
      if (!raw) { document.getElementById('status').textContent = 'Bulk input wajib diisi.'; return; }
      let payload = null;
      let cleanRaw = raw.replace(/,\s*([\]}])/g, '$1');
      try { payload = JSON.parse(cleanRaw); } catch(e) {
        try { payload = JSON.parse('[' + cleanRaw + ']'); } catch(e2) {
          document.getElementById('status').textContent = 'JSON bulk tidak valid.'; return;
        }
      }
      if (!Array.isArray(payload)) payload = [payload];

      const queueItem = {
        queries: payload,
        alpha_dense: parseFloat(document.getElementById('alpha_dense').value),
        alpha_sparse: parseFloat(document.getElementById('alpha_sparse').value),
        candidate_pool: parseInt(document.getElementById('candidate_pool').value),
        alpha_ce: parseFloat(document.getElementById('alpha_ce').value),
      };

      try {
        const res = await fetch('/v3-queue', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(queueItem)
        });
        const data = await res.json();
        if (!res.ok) {
          document.getElementById('status').textContent = 'Error: ' + (data.error || 'Unknown');
          return;
        }
        document.getElementById('status').textContent = `Added to queue as ${data.label} (position ${data.queue_position})`;
        queueData.push({
          session_id: data.session_id,
          label: data.label,
          query_count: payload.length,
          params: { alpha_dense: queueItem.alpha_dense, alpha_sparse: queueItem.alpha_sparse, candidate_pool: queueItem.candidate_pool, alpha_ce: queueItem.alpha_ce },
          status: 'queued'
        });
        saveQueueUIState();
        renderQueueList();
        startPollingIfNeeded();
      } catch(e) {
        document.getElementById('status').textContent = 'Error: ' + e.message;
      }
    }

    async function removeQueueItem(index) {
      try {
        await fetch('/v3-queue/' + index, { method: 'DELETE' });
        refreshQueueList();
      } catch(e) {}
    }

    function setAqSessionMode(mode) {
      document.getElementById('aqSessionMode').value = mode;
      const btnNew = document.getElementById('aqSessionNew');
      const btnCont = document.getElementById('aqSessionContinue');
      if (mode === 'new') {
        btnNew.style.background = '#4caf50'; btnNew.style.color = '#fff'; btnNew.style.borderColor = '#4caf50';
        btnCont.style.background = ''; btnCont.style.color = ''; btnCont.style.borderColor = '';
      } else {
        btnCont.style.background = '#4caf50'; btnCont.style.color = '#fff'; btnCont.style.borderColor = '#4caf50';
        btnNew.style.background = ''; btnNew.style.color = ''; btnNew.style.borderColor = '';
      }
    }

    function toggleAddQueryPanel() {
      const panel = document.getElementById('addQueryPanel');
      panel.style.display = panel.style.display === 'none' || !panel.style.display ? 'block' : 'none';
    }

    function loadJsonFile(event) {
      const file = event.target.files[0];
      if (!file) return;
      document.getElementById('fileName').textContent = file.name;
      const reader = new FileReader();
      reader.onload = function(e) {
        document.getElementById('addQueryInput').value = e.target.result;
      };
      reader.readAsText(file);
    }

    async function submitAddQuery() {
      const raw = document.getElementById('addQueryInput').value.trim();
      if (!raw) { document.getElementById('status').textContent = 'Input wajib diisi.'; return; }
      let payload = null;
      let cleanRaw = raw.replace(/,\s*([\]}])/g, '$1');
      try { payload = JSON.parse(cleanRaw); } catch(e) {
        try { payload = JSON.parse('[' + cleanRaw + ']'); } catch(e2) {
          document.getElementById('status').textContent = 'JSON tidak valid: ' + e.message;
          return;
        }
      }
      if (!Array.isArray(payload)) payload = [payload];
      if (payload.length === 0) { document.getElementById('status').textContent = 'Payload kosong.'; return; }

      const queueItem = {
        queries: payload,
        session_mode: document.getElementById('aqSessionMode').value,
        alpha_dense: parseFloat(document.getElementById('aq_alpha_dense').value),
        alpha_sparse: parseFloat(document.getElementById('aq_alpha_sparse').value),
        candidate_pool: parseInt(document.getElementById('aq_candidate_pool').value),
        alpha_ce: parseFloat(document.getElementById('aq_alpha_ce').value),
      };

      try {
        const res = await fetch('/v3-queue', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(queueItem)
        });
        const data = await res.json();
        if (!res.ok) {
          document.getElementById('status').textContent = 'Error: ' + (data.error || 'Unknown');
          return;
        }
        document.getElementById('status').textContent = `Added to queue as ${data.label} (${payload.length} queries)`;
        document.getElementById('addQueryInput').value = '';
        document.getElementById('fileName').textContent = 'No file selected';
        document.getElementById('jsonFileInput').value = '';
        toggleAddQueryPanel();
        refreshQueueList();
        startPollingIfNeeded();
      } catch(e) {
        document.getElementById('status').textContent = 'Error: ' + e.message;
      }
    }

    async function clearQueue() {
      try {
        await fetch('/v3-queue', { method: 'DELETE' });
        queueData = [];
        saveQueueUIState();
        renderQueueList();
      } catch(e) {}
    }

    async function refreshQueueList() {
      try {
        const res = await fetch('/v3-queue');
        const data = await res.json();
        queueData = (data.items || []).map((item, i) => ({
          session_id: item.session_id,
          label: item.label || 'Session ' + item.session_id,
          query_count: item.query_count || (item.queries || []).length,
          params: item.params || {},
          session_mode: item.session_mode || 'new',
          status: 'queued'
        }));
        saveQueueUIState();
        renderQueueList(data.running);
      } catch(e) {}
    }

    function renderQueueList(isRunning) {
      const container = document.getElementById('queueList');
      const empty = document.getElementById('queueEmpty');
      if (!queueData || queueData.length === 0) {
        container.innerHTML = '';
        empty.style.display = 'block';
        return;
      }
      empty.style.display = 'none';
      let html = '';
      queueData.forEach((item, i) => {
        const isActive = i === 0 && isRunning;
        const cls = isActive ? 'active' : '';
        html += '<div class="queue-item ' + cls + '">';
        html += '<div class="queue-header">';
        html += '<h4>' + (item.label || 'Queue ' + (i+1));
        if (isActive) html += ' <span class="spinner"></span> Processing...';
        html += '</h4>';
        html += '<button class="queue-remove" onclick="removeQueueItem(' + i + ')">Remove</button>';
        html += '</div>';
        html += '<div class="small">' + item.query_count + ' queries | Session: ' + (item.session_mode === 'continue' ? 'Continue Last' : 'New') + ' | alpha_dense=' + (item.params.alpha_dense||0.6) + ' alpha_sparse=' + (item.params.alpha_sparse||0.4) + ' candidate_pool=' + (item.params.candidate_pool||10) + ' alpha_ce=' + (item.params.alpha_ce||0.8) + '</div>';
        html += '</div>';
      });
      container.innerHTML = html;
    }

    function startPollingIfNeeded() {
      if (v3PollInterval) return;
      const progressWrap = document.getElementById('progressWrap');
      if (progressWrap.style.display !== 'block' || !document.getElementById('bulkBtnV3').disabled) {
        document.getElementById('bulkBtnV3').disabled = true;
        progressWrap.style.display = 'block';
      }
      v3PollInterval = setInterval(async () => {
        await pollV3Progress();
        refreshQueueList();
      }, 500);
    }

    // On page load: restore state
    (async function init() {
      loadQueueUIState();
      await refreshQueueList();

      // Check current progress
      try {
        const res = await fetch('/progress');
        const p = await res.json();
        if (p.running) {
          document.getElementById('progressWrap').style.display = 'block';
          document.getElementById('bulkBtnV3').disabled = true;
          v3PollInterval = setInterval(async () => {
            await pollV3Progress();
            refreshQueueList();
          }, 500);
        } else if (p.current > 0 && p.finished_at) {
          document.getElementById('progressWrap').style.display = 'block';
          const sid = p.session_id == null ? 'N/A' : p.session_id;
          document.getElementById('progressText').textContent = `Last session ${sid}: ${p.current}/${p.total} queries completed.`;
          document.getElementById('progressBar').style.width = '100%';
        }
      } catch(e) {}

      // Auto-refresh queue every 3s
      setInterval(refreshQueueList, 3000);
    })();
  </script>
</body>
</html>
"""


INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V1 Hybrid Research Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; color: #222; }
    textarea { width: 100%; border: 1px solid #ccc; border-radius: 6px; padding: 8px; }
    #query { height: 80px; margin-bottom: 8px; }
    #bulkInput { height: 180px; font-family: Consolas, monospace; }
    .inline-options { display: flex; gap: 16px; align-items: center; margin: 8px 0; font-size: 13px; }
    .actions { display: flex; gap: 8px; margin: 10px 0; flex-wrap: wrap; }
    button, a.btn { padding: 8px 14px; border: 1px solid #bbb; background: #f7f7f7; border-radius: 6px; cursor: pointer; text-decoration: none; color: #222; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .section { margin-top: 16px; }
    .summary { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px; padding: 12px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }
    th { background: #f3f3f3; }
    tr.top-row { background: #eafbe7; }
    tr.data-row { cursor: pointer; }
    .mono { font-family: Consolas, monospace; }
    .small { font-size: 12px; color: #555; }
    #status { margin-top: 6px; font-size: 13px; color: #444; }
    #progressWrap { margin-top: 8px; background: #eee; border-radius: 8px; overflow: hidden; height: 18px; border: 1px solid #ddd; }
    #progressBar { width: 0%; height: 100%; background: #4caf50; transition: width 0.2s ease; }
    #progressText { margin-top: 6px; font-size: 12px; color: #333; }
    #bulkResults { margin-top: 16px; }
    .bulk-item { background: #fafafa; border: 1px solid #ddd; border-radius: 6px; padding: 12px; margin-bottom: 12px; }
    .bulk-item h4 { margin: 0 0 8px 0; }
    .result-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 8px; }
    .result-col h5 { margin: 0 0 4px 0; font-size: 12px; background: #eee; padding: 4px 6px; border-radius: 4px; }
    .result-col table { margin: 0; font-size: 11px; }
    .result-col th, .result-col td { padding: 4px 6px; }
    .query-meta { font-size: 11px; color: #666; margin-top: 4px; }
    #modalOverlay { display: none; position: fixed; z-index: 20; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.45); }
    #modalBox { background: #fff; width: min(800px, 90%); margin: 6% auto; border-radius: 8px; padding: 16px; border: 1px solid #ddd; }
    #modalClose { float: right; border: 0; background: transparent; font-size: 20px; cursor: pointer; }
  </style>
</head>
<body>
  <h2>RAG V1 Hybrid - Research Evaluation Platform</h2>

  <div class="section">
    <h3>Single Query</h3>
    <textarea id="query" placeholder="Masukkan query..."></textarea>
    <textarea id="gtSingle" placeholder='Ground truth ranked (JSON array), contoh: ["A.5.11"]'></textarea>
    <div class="actions">
      <button onclick="runSingle()">Run Query</button>
      <a class="btn" href="/history" target="_blank">Open History</a>
    </div>
  </div>

  <div class="section">
    <h3>Bulk Input (V3 Pipeline)</h3>
    <textarea id="bulkInput" placeholder='[{"query_id":"Q1","query":"...","ground_truth_ranked":["A.5.18","A.5.16","A.5.15"]}]'></textarea>
    <div style="margin: 10px 0;">
      <label><strong>Session Mode:</strong></label>
      <div class="actions" style="margin-top: 8px;">
        <button id="sessionNewBtn" onclick="setSessionMode('new')" style="background: #e8f5e9;">Start New Session</button>
        <button id="sessionContinueBtn" onclick="setSessionMode('continue')" style="background: #fff3e0;">Continue Session</button>
      </div>
      <div id="sessionInfo" class="summary" style="margin-top: 8px; font-size: 13px;">
        Loading session info...
      </div>
    </div>
    <div class="actions">
      <button id="bulkBtnV3" onclick="runBulkV3()">Run Bulk V3 Evaluation</button>
      <button id="addQueueBtn" onclick="addToQueue()">Add to Queue</button>
    </div>
    <div class="actions">
      <button id="bulkBtnDSH" onclick="runBulk(['dense','sparse','hybrid'])">Run Bulk Evaluation D-S-H</button>
      <button id="bulkBtnSDH" onclick="runBulk(['sparse','dense','hybrid'])">Run Bulk Evaluation S-D-H</button>
      <button id="bulkBtnHDS" onclick="runBulk(['hybrid','dense','sparse'])">Run Bulk Evaluation H-D-S</button>
      <button id="bulkBtnDenseOnly" onclick="runBulk(['dense'], true)">Run Bulk Evaluation Dense Only</button>
      <button id="bulkBtnSparseOnly" onclick="runBulk(['sparse'], true)">Run Bulk Evaluation Sparse Only</button>
      <button id="bulkBtnHybridOnly" onclick="runBulk(['hybrid'], true)">Run Bulk Evaluation Hybrid Only</button>
    </div>
    <div id="progressWrap"><div id="progressBar"></div></div>
    <div id="progressText">Progress: 0% (Idle)</div>
    <div id="bulkResults"></div>
  </div>

  <div id="status"></div>

  <div class="section summary">
    <div><b>Top Hybrid:</b> <span id="topControl">-</span></div>
    <div><b>Answer:</b></div>
    <pre id="answerBox" class="mono small" style="max-height:220px;overflow:auto;">-</pre>
  </div>

  <div class="section"><h3>Dense Results</h3><div id="denseTable"></div></div>
  <div class="section"><h3>Sparse Results</h3><div id="sparseTable"></div></div>
  <div class="section"><h3>Hybrid Results</h3><div id="hybridTable"></div></div>

  <div id="modalOverlay" onclick="closeModal()">
    <div id="modalBox" onclick="event.stopPropagation()">
      <button id="modalClose" onclick="closeModal()">×</button>
      <h3 id="modalTitle">Control Detail</h3>
      <p><b>Objective</b></p><p id="modalObjective"></p>
      <p><b>Description</b></p><p id="modalDescription"></p>
    </div>
  </div>

  <script>
    function fmtScore(v) { return Number(v || 0).toFixed(3); }
    function fmtTime(v) {
      const n = Number(v || 0);
      if (n < 0.001) return `${(n * 1_000_000).toFixed(0)}µs`;
      if (n < 1) return `${(n * 1000).toFixed(3)}ms`;
      return `${n.toFixed(3)}s`;
    }
    function openModal(item) {
      document.getElementById('modalTitle').textContent = `${item.control_id} - ${item.title}`;
      document.getElementById('modalObjective').textContent = item.objective || '-';
      document.getElementById('modalDescription').textContent = item.description || '-';
      document.getElementById('modalOverlay').style.display = 'block';
    }
    function closeModal() { document.getElementById('modalOverlay').style.display = 'none'; }

    function renderTable(targetId, rows) {
      const target = document.getElementById(targetId);
      if (!rows || rows.length === 0) { target.innerHTML = '<div class="small">No results.</div>'; return; }
      const html = rows.map((r, idx) => `
        <tr class="data-row ${idx===0 ? 'top-row' : ''}" data-idx="${idx}">
          <td>${r.control_id} - ${r.title}</td>
          <td class="mono">${fmtScore(r.score || 0)}</td>
        </tr>`).join('');
      target.innerHTML = `<table><thead><tr><th>Control</th><th>Score</th></tr></thead><tbody>${html}</tbody></table>`;
      target.querySelectorAll('tr.data-row').forEach((tr) => tr.addEventListener('click', () => openModal(rows[Number(tr.getAttribute('data-idx'))])));
    }

    function renderBulkResults(results) {
      const container = document.getElementById('bulkResults');
      if (!results || results.length === 0) {
        container.innerHTML = '<div class="small">No bulk results yet.</div>';
        return;
      }
      const html = results.map((r, idx) => {
        const renderCol = (title, results, scoreKey) => {
          const rowsHtml = (results || []).map((item, i) => `
            <tr class="${i===0 ? 'top-row' : ''} data-row" data-idx="${i}">
              <td>${item.control_id}</td>
              <td class="mono">${fmtScore(item.score)}</td>
            </tr>`).join('');
          return `
            <div class="result-col">
              <h5>${title}</h5>
              <table><thead><tr><th>ID</th><th>Score</th></tr></thead><tbody>${rowsHtml}</tbody></table>
            </div>`;
        };
        return `
          <div class="bulk-item">
            <h4>${r.query_id || 'Q' + (idx+1)}: ${r.query}</h4>
            <div class="query-meta">
              Method: ${(r.method_name || (Array.isArray(r.method_order) ? r.method_order.join('-') : '-')).toUpperCase()} |
              GT: [${(r.ground_truth_ranked || []).join(', ')}] |
              Dense H:${fmtScore(r.metrics?.dense?.hit)} R:${fmtScore(r.metrics?.dense?.recall)} MRR:${fmtScore(r.metrics?.dense?.mrr)} |
              Sparse H:${fmtScore(r.metrics?.sparse?.hit)} R:${fmtScore(r.metrics?.sparse?.recall)} MRR:${fmtScore(r.metrics?.sparse?.mrr)} |
              Hybrid H:${fmtScore(r.metrics?.hybrid?.hit)} R:${fmtScore(r.metrics?.hybrid?.recall)} MRR:${fmtScore(r.metrics?.hybrid?.mrr)} |
              Time: ${fmtTime(r.timings?.total_time)}
            </div>
            <div class="result-grid">
              ${renderCol('Dense', r.dense_results, 'dense_score')}
              ${renderCol('Sparse', r.sparse_results, 'sparse_score')}
              ${renderCol('Hybrid', r.hybrid_results, 'hybrid_score')}
            </div>
          </div>`;
      }).join('');
      container.innerHTML = html;
      container.querySelectorAll('.bulk-item .data-row').forEach((tr) => {
        tr.addEventListener('click', () => {
          const itemIdx = Number(tr.getAttribute('data-idx'));
          const col = tr.closest('.result-col');
          const colType = col.querySelector('h5').textContent.toLowerCase();
          const resultItem = results[Math.floor(tr.closest('.bulk-item').querySelector('.result-grid').parentElement.getAttribute('data-idx'))];
          const targetResults = colType === 'dense' ? resultItem.dense_results : colType === 'sparse' ? resultItem.sparse_results : resultItem.hybrid_results;
          if (targetResults && targetResults[itemIdx]) openModal(targetResults[itemIdx]);
        });
      });
    }

    let pollInterval = null;
    function setBulkButtonsDisabled(disabled) {
      ['bulkBtnDSH', 'bulkBtnSDH', 'bulkBtnHDS', 'bulkBtnDenseOnly', 'bulkBtnSparseOnly', 'bulkBtnHybridOnly'].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.disabled = disabled;
      });
    }
    async function refreshSessionInfo() {
      try {
        const res = await fetch('/session-info');
        const data = await res.json();
        const latest = data.latest_session_id == null ? '-' : data.latest_session_id;
        document.getElementById('sessionInfo').textContent = `Current Session: ${latest}`;
      } catch (_) {}
    }
    async function pollProgress() {
      try {
        const res = await fetch('/progress');
        const p = await res.json();
        document.getElementById('progressBar').style.width = `${p.percentage}%`;
        const sid = p.session_id == null ? '-' : p.session_id;
        const order = Array.isArray(p.method_order) ? p.method_order.join('-').toUpperCase() : '-';
        document.getElementById('progressText').textContent = `Session ${sid} | Order ${order} | Processing Query ${p.current} / ${p.total}... (${p.percentage}%) - ${p.status}`;
        if (p.bulk_results && p.bulk_results.length > 0) {
          renderBulkResults(p.bulk_results);
        }
        if (p.error) {
          document.getElementById('status').textContent = 'Error: ' + p.error;
          clearInterval(pollInterval);
          setBulkButtonsDisabled(false);
          refreshSessionInfo();
          return;
        }
        if (!p.running && p.current > 0) {
          clearInterval(pollInterval);
          document.getElementById('status').textContent = `Bulk completed. Session ${sid}. Processed: ${p.current} queries.`;
          setBulkButtonsDisabled(false);
          refreshSessionInfo();
        }
      } catch (e) {
        console.error('Poll error:', e);
      }
    }

    async function runSingle() {
      const status = document.getElementById('status');
      const query = document.getElementById('query').value.trim();
      if (!query) { status.textContent = 'Query wajib diisi.'; return; }

      let gt = [];
      const gtRaw = document.getElementById('gtSingle').value.trim();
      if (gtRaw) {
        try { gt = JSON.parse(gtRaw); } catch { status.textContent = 'Ground truth ranked bukan JSON valid.'; return; }
        if (!Array.isArray(gt)) { status.textContent = 'Ground truth ranked harus array.'; return; }
      }

      status.textContent = 'Processing query...';
      try {
        const res = await fetch('/query', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ query, ground_truth_ranked: gt })
        });
        const data = await res.json();
        if (!res.ok) { status.textContent = 'Error: ' + (data.error || 'Unknown'); return; }
        const top = (data.hybrid_results && data.hybrid_results[0]) || null;
        document.getElementById('topControl').textContent = top ? `${top.control_id} - ${top.title}` : '-';
        document.getElementById('answerBox').textContent = typeof data.answer === 'string' ? data.answer : JSON.stringify(data.answer, null, 2);
        renderTable('denseTable', data.dense_results || []);
        renderTable('sparseTable', data.sparse_results || []);
        renderTable('hybridTable', data.hybrid_results || []);
        status.textContent = 'Done.';
      } catch (e) {
        status.textContent = 'Error: ' + e.message;
      }
    }

    async function runBulk(methodOrder, singleMethod = false) {
      const status = document.getElementById('status');
      const raw = document.getElementById('bulkInput').value.trim();
      if (!raw) { status.textContent = 'Bulk input wajib diisi.'; return; }
      let payload = null;
      try { payload = JSON.parse(raw); } catch { status.textContent = 'JSON bulk tidak valid.'; return; }
      if (!Array.isArray(payload)) { status.textContent = 'Payload bulk harus array.'; return; }
      const sessionModeEl = document.querySelector('input[name="sessionMode"]:checked');
      const sessionMode = sessionModeEl ? sessionModeEl.value : 'continue';

      status.textContent = 'Starting bulk evaluation...';
      setBulkButtonsDisabled(true);
      document.getElementById('bulkResults').innerHTML = '';

      try {
        const res = await fetch('/bulk-query', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ items: payload, method_order: methodOrder, session_mode: sessionMode, single_method: singleMethod })
        });
        const data = await res.json();
        if (!res.ok) {
          status.textContent = 'Bulk error: ' + (data.error || 'Unknown');
          setBulkButtonsDisabled(false);
          return;
        }
        const sid = data.session_id == null ? '-' : data.session_id;
        status.textContent = `Bulk started. Session ${sid}.`;
        pollInterval = setInterval(pollProgress, 500);
      } catch (e) {
        status.textContent = 'Bulk error: ' + e.message;
        setBulkButtonsDisabled(false);
      }
    }
    refreshSessionInfo();
  </script>
</body>
</html>
"""


HISTORY_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V1 - Session History</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 16px; color: #222; }
    .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; table-layout: fixed; }
    th, td { border: 1px solid #ddd; padding: 7px; text-align: left; font-size: 12px; vertical-align: top; word-wrap: break-word; }
    th { background: #f3f3f3; }
    .compact { max-width: 350px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .cell-list { display: flex; flex-direction: column; gap: 3px; }
    .item { cursor: pointer; border-radius: 4px; padding: 2px 4px; }
    .item.top1 { font-weight: bold; }
    .item.correct { background: #e8f7e8; color: #176c17; }
    .item.wrong { background: #fdecec; color: #8a2323; }
    .gt-tag { display: inline-block; margin: 1px 4px 1px 0; padding: 2px 6px; border-radius: 12px; background: #f2f2f2; }
    .summary { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px; padding: 10px; margin-bottom: 12px; }
    .best { background: #eafbe7; }
    .mono { font-family: Consolas, monospace; white-space: pre-line; }
    .btn-reset { padding: 8px 14px; border: 1px solid #d73a49; background: #fff; border-radius: 6px; cursor: pointer; color: #d73a49; }
    .btn-reset:hover { background: #fff5f5; }
    #modalOverlay { display: none; position: fixed; z-index: 20; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.45); }
    #modalBox { background: #fff; width: min(800px, 90%); margin: 6% auto; border-radius: 8px; padding: 16px; border: 1px solid #ddd; }
    #modalClose { float: right; border: 0; background: transparent; font-size: 20px; cursor: pointer; }
  </style>
</head>
<body>
  <div class="header-actions">
    <h2>History Evaluation - Session {{ session_id }}</h2>
    <div>
      <a class="btn" href="/">← Back to Dashboard</a>
      <a class="btn" href="/history">All Sessions</a>
      <button class="btn-reset" onclick="resetHistory()">Reset History</button>
    </div>
  </div>

  <div class="summary">
    <h3 style="margin:0 0 8px 0;">Overall Performance</h3>
    <table>
      <thead><tr><th>Method</th><th>Hit@3</th><th>Recall@3</th><th>Precision@3</th><th>MRR</th><th>Avg Time</th></tr></thead>
      <tbody>
        {% for method in ['dense', 'sparse', 'hybrid'] %}
        <tr class="{{ 'best' if best_method == method else '' }}">
          <td>{{ method|capitalize }}</td>
          <td>{{ '%.3f'|format(summary[method]['hit']) }}</td>
          <td>{{ '%.3f'|format(summary[method]['recall']) }}</td>
          <td>{{ '%.3f'|format(summary[method]['precision']) }}</td>
          <td>{{ '%.3f'|format(summary[method]['mrr']) }}</td>
          <td>{{ format_duration(summary[method]['avg_time']) }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width:18%">Query</th>
        <th style="width:15%">Dense</th>
        <th style="width:15%">Sparse</th>
        <th style="width:15%">Hybrid</th>
        <th style="width:11%">Ground Truth</th>
        <th style="width:14%">Metrics</th>
        <th style="width:12%">Time</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td class="compact" title="{{ r.query_id or '' }} {{ r.query }}">
          <b>{{ r.query_id or '-' }}</b><br/>{{ r.query }}
        </td>
        <td><div class="cell-list">{% for item in r.dense_view %}<div class="item {{ 'top1' if item.is_top1 else '' }} {{ 'correct' if item.is_match else 'wrong' }}" data-control-id="{{ item.control_id }}">{{ '🟢' if item.is_match else '🔴' }} {{ item.text }}</div>{% endfor %}</div></td>
        <td><div class="cell-list">{% for item in r.sparse_view %}<div class="item {{ 'top1' if item.is_top1 else '' }} {{ 'correct' if item.is_match else 'wrong' }}" data-control-id="{{ item.control_id }}">{{ '🟢' if item.is_match else '🔴' }} {{ item.text }}</div>{% endfor %}</div></td>
        <td><div class="cell-list">{% for item in r.hybrid_view %}<div class="item {{ 'top1' if item.is_top1 else '' }} {{ 'correct' if item.is_match else 'wrong' }}" data-control-id="{{ item.control_id }}">{{ '🟢' if item.is_match else '🔴' }} {{ item.text }}</div>{% endfor %}</div></td>
        <td>{% for gt in r.ground_truth %}<span class="gt-tag">{{ gt }}</span>{% endfor %}</td>
        <td class="mono">
Dense → H:{{ '%.2f'|format(r.dense_hit or 0) }} R:{{ '%.2f'|format(r.dense_recall or 0) }} P:{{ '%.2f'|format(r.dense_precision or 0) }} MRR:{{ '%.3f'|format(r.dense_mrr or 0) }}
Sparse → H:{{ '%.2f'|format(r.sparse_hit or 0) }} R:{{ '%.2f'|format(r.sparse_recall or 0) }} P:{{ '%.2f'|format(r.sparse_precision or 0) }} MRR:{{ '%.3f'|format(r.sparse_mrr or 0) }}
Hybrid → H:{{ '%.2f'|format(r.hybrid_hit or 0) }} R:{{ '%.2f'|format(r.hybrid_recall or 0) }} P:{{ '%.2f'|format(r.hybrid_precision or 0) }} MRR:{{ '%.3f'|format(r.hybrid_mrr or 0) }}
        </td>
        <td class="mono">
Dense: {{ format_duration(r.dense_time or 0) }}
Sparse: {{ format_duration(r.sparse_time or 0) }}
Hybrid: {{ format_duration(r.hybrid_time or 0) }}
Total: {{ format_duration(r.total_time or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div id="modalOverlay" onclick="closeModal()">
    <div id="modalBox" onclick="event.stopPropagation()">
      <button id="modalClose" onclick="closeModal()">×</button>
      <h3 id="modalTitle">Control Detail</h3>
      <p><b>Objective</b></p><p id="modalObjective"></p>
      <p><b>Description</b></p><p id="modalDescription"></p>
    </div>
  </div>

  <script>
    const controlCatalog = {{ control_catalog|safe }};
    function openModal(controlId) {
      const info = controlCatalog[controlId];
      if (!info) return;
      document.getElementById('modalTitle').textContent = `${controlId} - ${info.title || '-'}`;
      document.getElementById('modalObjective').textContent = info.objective || '-';
      document.getElementById('modalDescription').textContent = info.description || '-';
      document.getElementById('modalOverlay').style.display = 'block';
    }
    function closeModal() { document.getElementById('modalOverlay').style.display = 'none'; }
    document.querySelectorAll('.item[data-control-id]').forEach((el) => {
      el.addEventListener('click', () => openModal(el.getAttribute('data-control-id')));
    });

    async function resetHistory() {
      if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) return;
      try {
        const res = await fetch('/history', { method: 'DELETE' });
        if (res.ok) {
          window.location.reload();
        } else {
          const data = await res.json();
          alert('Failed to reset history: ' + (data.error || 'Unknown error'));
        }
      } catch (e) {
        alert('Failed to reset history: ' + e.message);
      }
    }
  </script>
</body>
</html>
"""


HISTORY_INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V1 - Sessions</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; color: #222; }
    .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    a.btn { padding: 8px 14px; border: 1px solid #bbb; background: #f7f7f7; border-radius: 6px; text-decoration: none; color: #222; }
    .session-list { display: flex; flex-direction: column; gap: 8px; max-width: 700px; }
    .session-item { display: block; padding: 12px; border: 1px solid #ddd; border-radius: 8px; text-decoration: none; color: #222; background: #fafafa; }
    .session-item:hover { background: #f1f7ff; border-color: #aac7ff; }
    .small { font-size: 12px; color: #555; }
    .btn-reset { padding: 8px 14px; border: 1px solid #d73a49; background: #fff; border-radius: 6px; cursor: pointer; color: #d73a49; }
    .btn-reset:hover { background: #fff5f5; }
  </style>
</head>
<body>
  <div class="header-actions">
    <h2>History Sessions</h2>
    <div>
      <a class="btn" href="/">← Back to Dashboard</a>
      <button class="btn-reset" onclick="resetHistory()">Reset History</button>
    </div>
  </div>
  {% if sessions %}
  <div class="session-list">
    {% for s in sessions %}
    <a class="session-item" href="/history/{{ s.session_id }}">
      <div><b>Session {{ s.session_id }}</b> ({{ s.row_count }} rows)</div>
      <div class="small">Start: {{ s.started_at }} | End: {{ s.finished_at }}</div>
    </a>
    {% endfor %}
  </div>
  {% if legacy_count > 0 %}
  <div class="session-list" style="margin-top: 12px;">
    <a class="session-item" href="/history/legacy">
      <div><b>Legacy (No Session)</b> ({{ legacy_count }} rows)</div>
      <div class="small">Records created before session_id support.</div>
    </a>
  </div>
  {% endif %}
  {% else %}
  <div class="small">No sessioned records yet. Run bulk evaluation first.</div>
  {% if legacy_count > 0 %}
  <div class="session-list" style="margin-top: 12px;">
    <a class="session-item" href="/history/legacy">
      <div><b>Legacy (No Session)</b> ({{ legacy_count }} rows)</div>
      <div class="small">Records created before session_id support.</div>
    </a>
  </div>
  {% endif %}
  {% endif %}
  <script>
    async function resetHistory() {
      if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) return;
      try {
        const res = await fetch('/history', { method: 'DELETE' });
        if (res.ok) {
          window.location.reload();
        } else {
          const data = await res.json();
          alert('Failed to reset history: ' + (data.error || 'Unknown error'));
        }
      } catch (e) {
        alert('Failed to reset history: ' + e.message);
      }
    }
  </script>
</body>
</html>
"""


HISTORY_V3_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V3 - Session History</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 16px; color: #222; }
    .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; table-layout: fixed; }
    th, td { border: 1px solid #ddd; padding: 7px; text-align: left; font-size: 12px; vertical-align: top; word-wrap: break-word; }
    th { background: #f3f3f3; }
    .compact { max-width: 420px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .cell-list { display: flex; flex-direction: column; gap: 3px; }
    .item { cursor: pointer; border-radius: 4px; padding: 2px 4px; }
    .item.top1 { font-weight: bold; }
    .item.correct { background: #e8f7e8; color: #176c17; }
    .item.wrong { background: #fdecec; color: #8a2323; }
    .gt-tag { display: inline-block; margin: 1px 4px 1px 0; padding: 2px 6px; border-radius: 12px; background: #f2f2f2; }
    .summary { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px; padding: 10px; margin-bottom: 12px; }
    .mono { font-family: Consolas, monospace; white-space: pre-line; }
    .small { font-size: 11px; color: #666; }
    .btn-reset { padding: 8px 14px; border: 1px solid #d73a49; background: #fff; border-radius: 6px; cursor: pointer; color: #d73a49; }
    .btn-reset:hover { background: #fff5f5; }
    .best { background: #eafbe7; }
    .muted { color: #aaa; text-align: center; }
    #modalOverlay { display: none; position: fixed; z-index: 20; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.45); }
    #modalBox { background: #fff; width: min(800px, 90%); margin: 6% auto; border-radius: 8px; padding: 16px; border: 1px solid #ddd; }
    #modalClose { float: right; border: 0; background: transparent; font-size: 20px; cursor: pointer; }
  </style>
</head>
<body>
  <div class="header-actions">
    <h2>History Evaluation V3 - Session {{ session_id }}</h2>
    <div>
      <a class="btn" href="/">Back to Dashboard</a>
      <a class="btn" href="/history/v3">All V3 Sessions</a>
      <button class="btn-reset" onclick="resetHistory()">Reset V3 History</button>
    </div>
  </div>

  <div class="summary">
    <h3 style="margin:0 0 8px 0;">Overall Performance</h3>
    <table>
      <thead><tr><th>Method</th><th>Hit@3</th><th>Recall@3</th><th>Precision@3</th><th>MRR</th><th>NDCG@3</th><th>MAP@3</th><th>Avg Retrieval</th><th>Avg Rerank</th><th>Avg Total</th></tr></thead>
      <tbody>
        <tr>
          <td>Hybrid (before rerank)</td>
          <td>{{ '%.3f'|format(summary["hybrid"]["hit"]) }}</td>
          <td>{{ '%.3f'|format(summary["hybrid"]["recall"]) }}</td>
          <td>{{ '%.3f'|format(summary["hybrid"]["precision"]) }}</td>
          <td>{{ '%.3f'|format(summary["hybrid"]["mrr"]) }}</td>
          <td>{{ '%.3f'|format(summary["hybrid"]["ndcg"]) }}</td>
          <td>{{ '%.3f'|format(summary["hybrid"]["map"]) }}</td>
          <td>{{ format_duration(summary["timings"]["avg_retrieval_time"]) }}</td>
          <td class="muted">—</td>
          <td>{{ format_duration(summary["timings"]["avg_retrieval_time"]) }}</td>
        </tr>
        <tr class="best">
          <td><b>Reranked (BGE)</b></td>
          <td>{{ '%.3f'|format(summary["reranking"]["hit"]) }}</td>
          <td>{{ '%.3f'|format(summary["reranking"]["recall"]) }}</td>
          <td>{{ '%.3f'|format(summary["reranking"]["precision"]) }}</td>
          <td>{{ '%.3f'|format(summary["reranking"]["mrr"]) }}</td>
          <td>{{ '%.3f'|format(summary["reranking"]["ndcg"]) }}</td>
          <td>{{ '%.3f'|format(summary["reranking"]["map"]) }}</td>
          <td>{{ format_duration(summary["timings"]["avg_retrieval_time"]) }}</td>
          <td>{{ format_duration(summary["timings"]["avg_reranking_time"]) }}</td>
          <td>{{ format_duration(summary["timings"]["avg_total_time"]) }}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width:20%">Annex Query Input</th>
        <th style="width:20%">Hybrid Top-3</th>
        <th style="width:20%">Reranked Top-3 (BGE)</th>
        <th style="width:12%">Ground Truth</th>
        <th style="width:18%">Performance Accuracy</th>
        <th style="width:10%">Time</th>
        <th style="width:8%">Params</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td class="compact" title="{{ r.query_id or '' }} {{ r.query }}">
          <b>{{ r.query_id or '-' }}</b><br/>{{ r.query }}
        </td>
        <td><div class="cell-list">{% for item in r.hybrid_view %}<div class="item {{ 'top1' if item.is_top1 else '' }} {{ 'correct' if item.is_match else 'wrong' }}" data-control-id="{{ item.control_id }}">{{ '🟢' if item.is_match else '🔴' }} {{ item.text }}</div>{% endfor %}</div></td>
        <td><div class="cell-list">{% for item in r.reranking_view %}<div class="item {{ 'top1' if item.is_top1 else '' }} {{ 'correct' if item.is_match else 'wrong' }}" data-control-id="{{ item.control_id }}">{{ '🟢' if item.is_match else '🔴' }} {{ item.text }}</div>{% endfor %}</div></td>
        <td>{% for gt in r.ground_truth %}<span class="gt-tag">{{ gt }}</span>{% endfor %}{% if not r.ground_truth %}-{% endif %}</td>
        <td class="mono">{{ r.performance_accuracy }}</td>
        <td class="mono">Retrieval: {{ format_duration(r.retrieval_time or 0) }}<br/>Rerank: {{ format_duration(r.reranking_time or 0) }}<br/>Total: {{ format_duration(r.total_time or 0) }}</td>
        <td class="mono small" style="font-size:11px;">{% if r.params %}ad:{{ r.params.alpha_dense }}<br/>as:{{ r.params.alpha_sparse }}<br/>ce:{{ r.params.alpha_ce }}<br/>pool:{{ r.params.candidate_pool }}{% else %}default{% endif %}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div id="modalOverlay" onclick="closeModal()">
    <div id="modalBox" onclick="event.stopPropagation()">
      <button id="modalClose" onclick="closeModal()">×</button>
      <h3 id="modalTitle">Control Detail</h3>
      <p><b>Objective</b></p><p id="modalObjective"></p>
      <p><b>Description</b></p><p id="modalDescription"></p>
    </div>
  </div>

  <div class="summary" style="margin-top: 14px;">
    <h3 style="margin:0 0 6px 0;">Session Averages</h3>
    {% set s = summary["timings"] %}
    <div class="mono">Retrieval: {{ format_duration(s["avg_retrieval_time"]) }} | Reranking: {{ format_duration(s["avg_reranking_time"]) }} | Total: {{ format_duration(s["avg_total_time"]) }}</div>
  </div>

  <script>
    const controlCatalog = {{ control_catalog|safe }};
    function openModal(controlId) {
      const info = controlCatalog[controlId];
      if (!info) return;
      document.getElementById("modalTitle").textContent = `${controlId} - ${info.title || "-"}`;
      document.getElementById("modalObjective").textContent = info.objective || "-";
      document.getElementById("modalDescription").textContent = info.description || "-";
      document.getElementById("modalOverlay").style.display = "block";
    }
    function closeModal() { document.getElementById("modalOverlay").style.display = "none"; }
    document.querySelectorAll(".item[data-control-id]").forEach((el) => {
      el.addEventListener("click", () => openModal(el.getAttribute("data-control-id")));
    });

    async function resetHistory() {
      if (!confirm("Are you sure you want to clear all V3 history?")) return;
      const res = await fetch("/history/v3", { method: "DELETE" });
      if (res.ok) window.location.reload();
      else { const d = await res.json(); alert("Failed: " + (d.error || "Unknown")); }
    }
  </script>
</body>
</html>
"""


HISTORY_V3_INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V3 - Sessions</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; color: #222; }
    .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    a.btn { padding: 8px 14px; border: 1px solid #bbb; background: #f7f7f7; border-radius: 6px; text-decoration: none; color: #222; }
    .session-list { display: flex; flex-direction: column; gap: 8px; max-width: 700px; }
    .session-item { display: block; padding: 12px; border: 1px solid #ddd; border-radius: 8px; text-decoration: none; color: #222; background: #fafafa; }
    .session-item:hover { background: #f1f7ff; border-color: #aac7ff; }
    .small { font-size: 12px; color: #555; }
    .btn-reset { padding: 8px 14px; border: 1px solid #d73a49; background: #fff; border-radius: 6px; cursor: pointer; color: #d73a49; }
    .btn-reset:hover { background: #fff5f5; }
  </style>
</head>
<body>
  <div class="header-actions">
    <h2>V3 History Sessions</h2>
    <div>
      <a class="btn" href="/">Back to Dashboard</a>
      <button class="btn-reset" onclick="resetHistory()">Reset V3 History</button>
    </div>
  </div>
  {% if sessions %}
  <div class="session-list">
    {% for s in sessions %}
    <a class="session-item" href="/history/v3/{{ s.session_id }}">
      <div><b>Session {{ s.session_id }}</b> ({{ s.row_count }} rows)</div>
      <div class="small">Start: {{ s.started_at }} | End: {{ s.finished_at }}</div>
    </a>
    {% endfor %}
  </div>
  {% if legacy_count > 0 %}
  <div class="session-list" style="margin-top: 12px;">
    <a class="session-item" href="/history/v3/legacy">
      <div><b>Legacy (No Session)</b> ({{ legacy_count }} rows)</div>
      <div class="small">Records created before session_id support.</div>
    </a>
  </div>
  {% endif %}
  {% else %}
  <div class="small">No V3 records yet. Call POST /v3 first.</div>
  {% if legacy_count > 0 %}
  <div class="session-list" style="margin-top: 12px;">
    <a class="session-item" href="/history/v3/legacy">
      <div><b>Legacy (No Session)</b> ({{ legacy_count }} rows)</div>
      <div class="small">Records created before session_id support.</div>
    </a>
  </div>
  {% endif %}
  {% endif %}
  <script>
    async function resetHistory() {
      if (!confirm("Are you sure you want to clear all V3 history?")) return;
      const res = await fetch("/history/v3", { method: "DELETE" });
      if (res.ok) window.location.reload();
      else { const d = await res.json(); alert("Failed: " + (d.error || "Unknown")); }
    }
  </script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


@app.get("/progress")
def progress():
    with PROGRESS_LOCK:
        data = dict(PROGRESS_STATE)
    return jsonify(data)


@app.post("/query")
def query():
    body = request.get_json(silent=True) or {}
    query_text = str(body.get("query", "")).strip()
    query_id = body.get("query_id")
    gt_ranked = body.get("ground_truth_ranked")
    if gt_ranked is None:
        gt_ranked = body.get("ground_truth", [])

    if not query_text:
        return jsonify({"error": "query is required"}), 400
    if not isinstance(gt_ranked, list):
        return jsonify({"error": "ground_truth_ranked must be a list"}), 400

    k = int(body.get("k", TOP_K))
    method_order = body.get("method_order", DEFAULT_METHOD_ORDER)
    single_method = bool(body.get("single_method", False))
    session_id = body.get("session_id")
    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return jsonify({"error": "session_id must be integer"}), 400
    try:
        method_order = normalize_method_order(method_order, expected_count=1 if single_method else None)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        processed = _process_retrieval_only(
            query_id=query_id,
            query=query_text,
            ground_truth_ranked=gt_ranked,
            k=k,
            method_order=method_order,
            session_id=session_id,
            single_method=single_method,
        )
        llm_result = pipeline.run(query=query_text, k=k)
        response = {
            "query_id": query_id,
            "query": query_text,
            "dense_results": processed["dense_results"],
            "sparse_results": processed["sparse_results"],
            "hybrid_results": processed["hybrid_results"],
            "ground_truth_ranked": gt_ranked,
            "metrics": processed["metrics"],
            "timings": processed["timings"],
            "method_order": processed["method_order"],
            "method_name": processed["method_name"],
            "session_id": processed["session_id"],
            "answer": llm_result.get("answer"),
            "llm_model": llm_result.get("llm_model"),
            "llm_error": llm_result.get("llm_error"),
            "fusion": {"method": "weighted_sum", "dense_weight": 0.6, "sparse_weight": 0.4},
        }
        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/v3")
def v3_ui():
    return render_template_string(V3_INDEX_HTML)


@app.post("/v3")
def query_v3():
    body = request.get_json(silent=True) or {}
    query_text = str(body.get("query", "")).strip()
    query_id = body.get("query_id")
    gt_ranked = body.get("ground_truth_ranked")
    if gt_ranked is None:
        gt_ranked = body.get("ground_truth")
    if not query_text:
        return jsonify({"error": "query is required"}), 400
    if gt_ranked is None:
        gt_ranked = V3_GROUND_TRUTH_BY_QUERY.get(query_text, [])
    if not isinstance(gt_ranked, list):
        return jsonify({"error": "ground_truth_ranked must be a list"}), 400
    gt_ranked = [str(x).strip() for x in gt_ranked if str(x).strip()]

    k = int(body.get("k", TOP_K))
    alpha_dense = body.get("alpha_dense")
    alpha_sparse = body.get("alpha_sparse")
    alpha_ce = body.get("alpha_ce")
    candidate_pool = body.get("candidate_pool")
    pipeline_params = {}
    if alpha_dense is not None:
        pipeline_params["alpha_dense"] = float(alpha_dense)
    if alpha_sparse is not None:
        pipeline_params["alpha_sparse"] = float(alpha_sparse)
    if alpha_ce is not None:
        pipeline_params["alpha_ce"] = float(alpha_ce)
    if candidate_pool is not None:
        pipeline_params["candidate_pool"] = int(candidate_pool)
    session_mode = str(body.get("session_mode", "continue"))
    session_id = body.get("session_id")
    if session_id is None:
        session_id = resolve_v3_session_id(session_mode)
    else:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return jsonify({"error": "session_id must be integer"}), 400

    try:
        result = pipeline_v3.run(query=query_text, k=k, **pipeline_params)
        hybrid_ids = [str(item.get("control_id", "")).strip() for item in result.get("hybrid_results", []) if str(item.get("control_id", "")).strip()]
        reranked_ids = [str(item.get("control_id", "")).strip() for item in result.get("reranked_results", []) if str(item.get("control_id", "")).strip()]
        hybrid_metrics = compute_metrics(hybrid_ids, gt_ranked, k=k)
        reranking_metrics = compute_metrics(reranked_ids, gt_ranked, k=k)
        timings = result.get("timings", {"retrieval_time": 0.0, "reranking_time": 0.0, "total_time": 0.0})
        save_history_row_v3(
            session_id=session_id,
            query_id=query_id,
            query=query_text,
            hybrid_results=result.get("hybrid_results", []),
            reranked_results=result.get("reranked_results", []),
            ground_truth_ranked=gt_ranked,
            hybrid_metrics=hybrid_metrics,
            reranking_metrics=reranking_metrics,
            timings=timings,
            params=result.get("params"),
        )
        return jsonify(
            {
                "query_id": query_id,
                "query": query_text,
                "hybrid_results": result.get("hybrid_results", []),
                "reranked_results": result.get("reranked_results", []),
                "ground_truth_ranked": gt_ranked,
                "metrics": {"hybrid": hybrid_metrics, "reranking": reranking_metrics},
                "answer": result.get("answer"),
                "llm_model": result.get("llm_model"),
                "llm_error": result.get("llm_error"),
                "fusion": result.get("fusion"),
                "timings": timings,
                "session_id": session_id,
                "method_name": "reranking",
                "params": result.get("params"),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def _process_v3_queue() -> None:
    global V3_BULK_THREAD
    try:
        while True:
            with V3_QUEUE_LOCK:
                if not V3_QUEUE:
                    break
                item = V3_QUEUE.pop(0)
                _save_v3_queue_unlocked()

            queries = item.get("queries", [])
            bulk_params = item.get("params", {})
            queue_label = item.get("label", "unknown")
            queue_idx = item.get("queue_index", 0)
            queue_total = item.get("queue_total", 1)
            session_mode = item.get("session_mode", "new")

            if not queries:
                continue

            session_id = resolve_v3_session_id(session_mode)
            queue_label = f"Session {session_id}"

            with PROGRESS_LOCK:
                PROGRESS_STATE["queue_index"] = queue_idx
                PROGRESS_STATE["queue_total"] = queue_total
                PROGRESS_STATE["queue_label"] = queue_label

            total = len(queries)
            reset_progress(total, session_id=session_id, method_order=["hybrid", "reranking"])

            with PROGRESS_LOCK:
                PROGRESS_STATE["queue_index"] = queue_idx
                PROGRESS_STATE["queue_total"] = queue_total
                PROGRESS_STATE["queue_label"] = queue_label

            for idx, q_item in enumerate(queries, start=1):
                query_text = str(q_item.get("query", "")).strip()
                query_id = q_item.get("query_id")
                gt_ranked = q_item.get("ground_truth_ranked", [])
                if not isinstance(gt_ranked, list):
                    gt_ranked = []
                gt_ranked = [str(x).strip() for x in gt_ranked if str(x).strip()]

                if not query_text:
                    set_progress(idx - 1, total, f"skipped empty query {idx}/{total}", True)
                    continue

                with PROGRESS_LOCK:
                    PROGRESS_STATE["queue_index"] = queue_idx
                    PROGRESS_STATE["queue_total"] = queue_total
                    PROGRESS_STATE["queue_label"] = queue_label

                set_progress(idx - 1, total, f"processing V3 query {idx}/{total}", True)

                try:
                    _bp = bulk_params or {}
                    result = pipeline_v3.run(query=query_text, k=TOP_K, **_bp)
                    hybrid_ids = [s["control_id"] for s in result.get("hybrid_results", [])]
                    reranked = result.get("reranked_results", [])
                    reranked_ids = [s["control_id"] for s in reranked]

                    hybrid_metrics = compute_metrics(
                        predicted_ids=hybrid_ids,
                        ground_truth_ranked=gt_ranked,
                        k=TOP_K,
                    )
                    reranking_metrics = compute_metrics(
                        predicted_ids=reranked_ids,
                        ground_truth_ranked=gt_ranked,
                        k=TOP_K,
                    )

                    raw_timings = result.get("timings", {})
                    timings = {
                        "retrieval_time": raw_timings.get("retrieval_time", 0.0),
                        "reranking_time": raw_timings.get("reranking_time", 0.0),
                        "total_time": raw_timings.get("total_time", 0.0),
                    }

                    save_history_row_v3(
                        session_id=session_id,
                        query_id=query_id,
                        query=query_text,
                        hybrid_results=result.get("hybrid_results", []),
                        reranked_results=reranked,
                        ground_truth_ranked=gt_ranked,
                        hybrid_metrics=hybrid_metrics,
                        reranking_metrics=reranking_metrics,
                        timings=timings,
                        params=result.get("params"),
                    )
                except Exception as exc:
                    import traceback
                    print(f"[bulk-v3-queue] Error on query {idx}: {exc}\n{traceback.format_exc()}")

                with PROGRESS_LOCK:
                    PROGRESS_STATE["queue_index"] = queue_idx
                    PROGRESS_STATE["queue_total"] = queue_total
                    PROGRESS_STATE["queue_label"] = queue_label

                set_progress(idx, total, f"processed V3 query {idx}/{total}", True)

            with V3_QUEUE_LOCK:
                has_more = bool(V3_QUEUE)
            if not has_more:
                set_progress(
                    PROGRESS_STATE["current"],
                    PROGRESS_STATE["total"],
                    "completed",
                    False,
                )

    except Exception as exc:
        import traceback
        set_progress(
            PROGRESS_STATE["current"],
            PROGRESS_STATE["total"],
            f"error: {exc}",
            False,
            str(exc) + "\n" + traceback.format_exc(),
        )
    finally:
        with PROGRESS_LOCK:
            PROGRESS_STATE["queue_index"] = None
            PROGRESS_STATE["queue_total"] = None
            PROGRESS_STATE["queue_label"] = None
        V3_BULK_THREAD = None


def _save_v3_queue_unlocked() -> None:
    data = {"items": V3_QUEUE, "session_counter": V3_QUEUE_SESSION_COUNTER}
    V3_QUEUE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_v3_queue_session_counter() -> None:
    with V3_QUEUE_LOCK:
        _save_v3_queue_unlocked()


@app.get("/v3-queue")
def get_v3_queue():
    with V3_QUEUE_LOCK:
        items = list(V3_QUEUE)
    return jsonify({"items": items, "running": PROGRESS_STATE["running"]})


@app.post("/v3-queue")
def add_v3_queue():
    global V3_BULK_THREAD
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Payload must be a JSON object"}), 400

    queries = body.get("queries", [])
    if not queries:
        return jsonify({"error": "queries array is empty"}), 400

    bulk_params = {
        "alpha_dense": body.get("alpha_dense"),
        "alpha_sparse": body.get("alpha_sparse"),
        "alpha_ce": body.get("alpha_ce"),
        "candidate_pool": body.get("candidate_pool"),
    }
    bulk_params = {k: v for k, v in bulk_params.items() if v is not None}

    session_mode = body.get("session_mode", "new")

    with V3_QUEUE_LOCK:
        queue_index = len(V3_QUEUE) + 1
        V3_QUEUE.append({
            "queries": queries,
            "params": bulk_params,
            "session_mode": session_mode,
            "label": f"Queue Item {queue_index}",
            "queue_index": queue_index,
            "query_count": len(queries),
        })
        total_in_queue = len(V3_QUEUE)
        for i, item in enumerate(V3_QUEUE):
            item["queue_index"] = i + 1
            item["queue_total"] = total_in_queue
        _save_v3_queue_unlocked()

    if not PROGRESS_STATE["running"] and V3_BULK_THREAD is None:
        V3_BULK_THREAD = threading.Thread(target=_process_v3_queue, daemon=True)
        V3_BULK_THREAD.start()

    return jsonify({
        "status": "queued",
        "queue_position": queue_index,
        "label": f"Queue Item {queue_index}",
    })


@app.delete("/v3-queue")
def clear_v3_queue():
    with V3_QUEUE_LOCK:
        V3_QUEUE.clear()
        _save_v3_queue_unlocked()
    return jsonify({"status": "cleared"})


@app.delete("/v3-queue/<int:index>")
def remove_v3_queue_item(index):
    with V3_QUEUE_LOCK:
        if 0 <= index < len(V3_QUEUE):
            V3_QUEUE.pop(index)
            total_in_queue = len(V3_QUEUE)
            for i, item in enumerate(V3_QUEUE):
                item["queue_index"] = i + 1
                item["queue_total"] = total_in_queue
            _save_v3_queue_unlocked()
            return jsonify({"status": "removed"})
        return jsonify({"error": "Index out of range"}), 404


@app.post("/bulk-v3")
def bulk_v3():
    global V3_BULK_THREAD
    body = request.get_json(silent=True)
    if isinstance(body, dict):
        queries = body.get("queries", [])
        session_mode = body.get("session_mode", "continue")
        bulk_params = {
            "alpha_dense": body.get("alpha_dense"),
            "alpha_sparse": body.get("alpha_sparse"),
            "alpha_ce": body.get("alpha_ce"),
            "candidate_pool": body.get("candidate_pool"),
        }
        bulk_params = {k: v for k, v in bulk_params.items() if v is not None}
    elif isinstance(body, list):
        queries = body
        session_mode = "continue"
        bulk_params = {}
    else:
        return jsonify({"error": "Payload must be a JSON array or object with 'queries'"}), 400
    
    if not queries:
        return jsonify({"error": "queries array is empty"}), 400

    if PROGRESS_STATE["running"]:
        return jsonify({"error": "Another bulk operation is already running"}), 400

    session_id = resolve_v3_session_id(session_mode)

    V3_BULK_THREAD = threading.Thread(target=_run_bulk_v3_in_background, args=(queries, session_id, bulk_params))
    V3_BULK_THREAD.start()

    return jsonify({
        "message": "V3 bulk processing started",
        "status": "started",
        "session_id": session_id,
    })


@app.post("/bulk-query")
def bulk_query():
    global BULK_THREAD
    body = request.get_json(silent=True)
    if isinstance(body, list):
        payload = body
        method_order = list(DEFAULT_METHOD_ORDER)
        session_mode = "continue"
        single_method = False
    elif isinstance(body, dict):
        payload = body.get("items")
        method_order = body.get("method_order", DEFAULT_METHOD_ORDER)
        session_mode = body.get("session_mode", "continue")
        single_method = bool(body.get("single_method", False))
    else:
        return jsonify({"error": "Payload must be a JSON array or object with 'items'"}), 400

    if not isinstance(payload, list):
        return jsonify({"error": "items must be a JSON array"}), 400

    try:
        order = normalize_method_order(method_order, expected_count=1 if single_method else None)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if single_method and len(order) != 1:
        return jsonify({"error": "Single-method evaluation expected exactly one method."}), 400

    session_id = resolve_session_id(str(session_mode))

    if PROGRESS_STATE["running"]:
        return jsonify({"error": "Another bulk operation is already running"}), 400

    BULK_THREAD = threading.Thread(target=_run_bulk_in_background, args=(payload, order, session_id, single_method))
    BULK_THREAD.start()

    return jsonify(
        {
            "message": "Bulk processing started",
            "status": "started",
            "session_id": session_id,
            "method_order": order,
            "single_method": single_method,
        }
    )


@app.get("/session-info")
def session_info():
    latest = get_latest_session_id()
    return jsonify({"latest_session_id": latest})


@app.get("/history/v3")
def history_index_v3():
    sessions = get_v3_session_summaries()
    legacy_count = get_v3_legacy_history_count()
    if request.args.get("format") == "json":
        return jsonify({"sessions": sessions, "legacy_count": legacy_count})
    return render_template_string(HISTORY_V3_INDEX_HTML, sessions=sessions, legacy_count=legacy_count)


@app.get("/history/v3/<slug>")
def history_by_slug_v3(slug: str):
    normalized = str(slug).strip().lower()
    if normalized == "legacy":
        rows = [r for r in get_history_rows_v3() if r.get("session_id") is None]
        session_label = "legacy"
    else:
        try:
            session_id = int(normalized)
        except ValueError:
            return jsonify({"error": "slug must be an integer session_id or 'legacy'"}), 400
        rows = get_history_rows_v3(session_id=session_id)
        session_label = session_id

    for row in rows:
        ground_truth = row.get("ground_truth", [])
        if not ground_truth:
            ground_truth = V3_GROUND_TRUTH_BY_QUERY.get(str(row.get("query", "")).strip(), [])
        row["ground_truth"] = ground_truth

        missing_hybrid_metrics = (
            row.get("hybrid_hit") is None
            or row.get("hybrid_recall") is None
            or row.get("hybrid_precision") is None
            or row.get("hybrid_mrr") is None
            or row.get("hybrid_ndcg") is None
        )
        if missing_hybrid_metrics and ground_truth:
            hybrid_ids = [str(item.get("control_id", "")).strip() for item in row.get("hybrid_results", []) if str(item.get("control_id", "")).strip()]
            hybrid_metrics = compute_metrics(hybrid_ids, ground_truth, k=TOP_K)
            row["hybrid_hit"] = hybrid_metrics["hit"]
            row["hybrid_recall"] = hybrid_metrics["recall"]
            row["hybrid_precision"] = hybrid_metrics["precision"]
            row["hybrid_mrr"] = hybrid_metrics["mrr"]
            row["hybrid_ndcg"] = hybrid_metrics["ndcg"]

        missing_reranking_metrics = (
            row.get("reranking_hit") is None
            or row.get("reranking_recall") is None
            or row.get("reranking_precision") is None
            or row.get("reranking_mrr") is None
            or row.get("reranking_ndcg") is None
        )
        if missing_reranking_metrics and ground_truth:
            reranked_ids = [str(item.get("control_id", "")).strip() for item in row.get("reranked_results", []) if str(item.get("control_id", "")).strip()]
            reranking_metrics = compute_metrics(reranked_ids, ground_truth, k=TOP_K)
            row["reranking_hit"] = reranking_metrics["hit"]
            row["reranking_recall"] = reranking_metrics["recall"]
            row["reranking_precision"] = reranking_metrics["precision"]
            row["reranking_mrr"] = reranking_metrics["mrr"]
            row["reranking_ndcg"] = reranking_metrics["ndcg"]

        row["hybrid_view"] = _view_for_v3_hybrid(row.get("hybrid_results", []), ground_truth)
        row["reranking_view"] = _view_for_v3_reranking(row.get("reranked_results", []), ground_truth)

        row["performance_accuracy"] = _format_accuracy_for_v3(row, k=TOP_K)

    summary = summarize_from_rows_v3(rows)
    query_time_rows = aggregate_v3_by_query(rows)

    if request.args.get("format") == "json":
        return jsonify(
            {
                "session_id": session_label,
                "rows": rows,
                "summary": summary,
                "query_time_rows": query_time_rows,
            }
        )

    return render_template_string(
        HISTORY_V3_HTML,
        session_id=session_label,
        rows=rows,
        summary=summary,
        query_time_rows=query_time_rows,
        control_catalog=json.dumps(CONTROL_CATALOG, ensure_ascii=False),
        format_duration=format_duration,
    )


@app.get("/history")
def history_index():
    sessions = get_session_summaries()
    legacy_count = get_legacy_history_count()
    if request.args.get("format") == "json":
        return jsonify({"sessions": sessions, "legacy_count": legacy_count})
    return render_template_string(HISTORY_INDEX_HTML, sessions=sessions, legacy_count=legacy_count)


@app.get("/history/<int:session_id>")
def history_by_session(session_id: int):
    rows = get_history_rows(session_id=session_id)
    summary = summarize_from_rows(rows)
    best_method = best_method_by_mrr(summary)

    for row in rows:
        gt = row.get("ground_truth", [])
        row["dense_view"] = _view_for_method(row.get("dense_results", []), gt)
        row["sparse_view"] = _view_for_method(row.get("sparse_results", []), gt)
        row["hybrid_view"] = _view_for_method(row.get("hybrid_results", []), gt)

    if request.args.get("format") == "json":
        return jsonify({"session_id": session_id, "rows": rows, "summary": summary, "best_method": best_method})

    return render_template_string(
        HISTORY_HTML,
        session_id=session_id,
        rows=rows,
        summary=summary,
        best_method=best_method,
        control_catalog=json.dumps(CONTROL_CATALOG, ensure_ascii=False),
        format_duration=format_duration,
    )


@app.get("/history/legacy")
def history_legacy():
    rows = get_history_rows()
    rows = [r for r in rows if r.get("session_id") is None]
    summary = summarize_from_rows(rows)
    best_method = best_method_by_mrr(summary)

    for row in rows:
        gt = row.get("ground_truth", [])
        row["dense_view"] = _view_for_method(row.get("dense_results", []), gt)
        row["sparse_view"] = _view_for_method(row.get("sparse_results", []), gt)
        row["hybrid_view"] = _view_for_method(row.get("hybrid_results", []), gt)

    return render_template_string(
        HISTORY_HTML,
        session_id="Legacy",
        rows=rows,
        summary=summary,
        best_method=best_method,
        control_catalog=json.dumps(CONTROL_CATALOG, ensure_ascii=False),
        format_duration=format_duration,
    )


@app.delete("/history")
def reset_history():
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM history")
            conn.commit()
        return jsonify({"message": "History cleared successfully"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.delete("/history/v3")
def reset_history_v3():
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM history_v3")
            conn.commit()
        return jsonify({"message": "V3 history cleared successfully"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    init_db()
    _load_v3_queue()
    app.run(host="127.0.0.1", port=5001, debug=True, threaded=True)
