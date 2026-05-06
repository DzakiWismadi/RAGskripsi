import json
import sqlite3
import sys
import threading
import time
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request

V2_ROOT = Path(__file__).resolve().parents[1] if '__file__' in locals() else Path.cwd()
V1_ROOT = V2_ROOT.parent / "ragV1"

# Add V2 to sys.path first (before V1)
sys.path.insert(0, str(V2_ROOT))
sys.path.insert(1, str(V1_ROOT))

# Direct import using sys.modules - load V2 modules explicitly
import importlib.util

# Load query_expansion module
qe_spec = importlib.util.spec_from_file_location("query_expansion", V2_ROOT / "query_expansion" / "query_expansion.py")
query_expansion_module = importlib.util.module_from_spec(qe_spec)
qe_spec.loader.exec_module(query_expansion_module)
query_expansion = query_expansion_module.query_expansion

# Load V2 pipeline module
v2_spec = importlib.util.spec_from_file_location("rag_pipeline_v2", V2_ROOT / "pipeline" / "rag_pipeline_v2.py")
v2_module = importlib.util.module_from_spec(v2_spec)
v2_spec.loader.exec_module(v2_module)
RAGPipelineV2 = v2_module.RAGPipelineV2

app = Flask(__name__)
pipeline = RAGPipelineV2(project_root=V2_ROOT)

DB_PATH = V2_ROOT / "rag_history_v2.db"
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
}
PROGRESS_LOCK = threading.Lock()
BULK_THREAD = None


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
            CREATE TABLE IF NOT EXISTS history_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT,
                original_query TEXT,
                expanded_query TEXT,
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
                llm_time REAL,
                retrieval_time REAL,
                total_time REAL,
                session_id INTEGER,
                method_order TEXT,
                method_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        for col_name, col_type in [
            ("query_id", "TEXT"), ("original_query", "TEXT"), ("expanded_query", "TEXT"),
            ("dense_results", "TEXT"), ("sparse_results", "TEXT"), ("hybrid_results", "TEXT"),
            ("ground_truth", "TEXT"),
            ("dense_hit", "REAL"), ("sparse_hit", "REAL"), ("hybrid_hit", "REAL"),
            ("dense_recall", "REAL"), ("sparse_recall", "REAL"), ("hybrid_recall", "REAL"),
            ("dense_precision", "REAL"), ("sparse_precision", "REAL"), ("hybrid_precision", "REAL"),
            ("dense_mrr", "REAL"), ("sparse_mrr", "REAL"), ("hybrid_mrr", "REAL"),
            ("llm_time", "REAL"), ("retrieval_time", "REAL"), ("total_time", "REAL"),
            ("session_id", "INTEGER"), ("method_order", "TEXT"), ("method_name", "TEXT"),
        ]:
            if not _column_exists(conn, "history_v2", col_name):
                conn.execute(f"ALTER TABLE history_v2 ADD COLUMN {col_name} {col_type}")
        conn.commit()


def load_control_catalog() -> dict[str, dict[str, str]]:
    controls_path = V1_ROOT / "data" / "iso_controls.json"
    controls = json.loads(controls_path.read_text(encoding="utf-8"))
    return {
        item["control_id"]: {
            "title": item.get("title", ""),
            "objective": item.get("objective", ""),
            "description": item.get("description", ""),
        }
        for item in controls
    }


CONTROL_CATALOG = load_control_catalog()


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
        row = conn.execute("SELECT MAX(session_id) AS latest FROM history_v2 WHERE session_id IS NOT NULL").fetchone()
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
            SELECT session_id, COUNT(*) AS row_count,
                   MIN(timestamp) AS started_at, MAX(timestamp) AS finished_at
            FROM history_v2 WHERE session_id IS NOT NULL
            GROUP BY session_id ORDER BY session_id DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def compact_results(results: list[dict[str, Any]], score_key: str, k: int = TOP_K) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in (results or [])[:k]:
        compact.append({
            "control_id": item.get("control_id", ""),
            "title": item.get("title", ""),
            "objective": item.get("objective", ""),
            "description": item.get("description", ""),
            "score": float(item.get(score_key, 0.0)),
        })
    return compact


def compute_metrics(predicted_ids: list[str], ground_truth_ranked: list[str], k: int = TOP_K) -> dict[str, float | None]:
    gt = [str(x).strip() for x in ground_truth_ranked if str(x).strip()]
    pred = [str(x).strip() for x in predicted_ids[:k] if str(x).strip()]
    if not gt:
        return {"hit": None, "recall": None, "precision": None, "mrr": None}
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
    return {"hit": hit, "recall": recall, "precision": precision, "mrr": mrr}


def save_history_row(
    session_id: int | None, method_name: str | None, query_id: str | None,
    original_query: str, expanded_query: str,
    dense_results: list[dict[str, Any]], sparse_results: list[dict[str, Any]], hybrid_results: list[dict[str, Any]],
    ground_truth_ranked: list[str],
    dense_metrics: dict[str, float | None], sparse_metrics: dict[str, float | None], hybrid_metrics: dict[str, float | None],
    timings: dict[str, float], method_order: list[str],
) -> None:
    with get_db_connection() as conn:
        conn.execute(
            """INSERT INTO history_v2 (
                session_id, method_order, method_name, query_id, original_query, expanded_query,
                dense_results, sparse_results, hybrid_results, ground_truth,
                dense_hit, sparse_hit, hybrid_hit,
                dense_recall, sparse_recall, hybrid_recall,
                dense_precision, sparse_precision, hybrid_precision,
                dense_mrr, sparse_mrr, hybrid_mrr,
                llm_time, retrieval_time, total_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, json.dumps(method_order), method_name, query_id, original_query, expanded_query,
             json.dumps(dense_results, ensure_ascii=False), json.dumps(sparse_results, ensure_ascii=False),
             json.dumps(hybrid_results, ensure_ascii=False), json.dumps(ground_truth_ranked, ensure_ascii=False),
             dense_metrics["hit"], sparse_metrics["hit"], hybrid_metrics["hit"],
             dense_metrics["recall"], sparse_metrics["recall"], hybrid_metrics["recall"],
             dense_metrics["precision"], sparse_metrics["precision"], hybrid_metrics["precision"],
             dense_metrics["mrr"], sparse_metrics["mrr"], hybrid_metrics["mrr"],
             float(timings.get("llm_time", 0.0)), float(timings.get("retrieval_time", 0.0)),
             float(timings.get("total_time", 0.0))),
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


def get_history_rows(limit: int = HISTORY_LIMIT, session_id: int | None = None) -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        if session_id is None:
            rows = conn.execute(
                """SELECT id, session_id, method_order, method_name, query_id, original_query, expanded_query,
                   dense_results, sparse_results, hybrid_results, ground_truth,
                   dense_hit, sparse_hit, hybrid_hit,
                   dense_recall, sparse_recall, hybrid_recall,
                   dense_precision, sparse_precision, hybrid_precision,
                   dense_mrr, sparse_mrr, hybrid_mrr,
                   llm_time, retrieval_time, total_time, timestamp
                FROM history_v2 ORDER BY id DESC LIMIT ?""", (limit,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, session_id, method_order, method_name, query_id, original_query, expanded_query,
                   dense_results, sparse_results, hybrid_results, ground_truth,
                   dense_hit, sparse_hit, hybrid_hit,
                   dense_recall, sparse_recall, hybrid_recall,
                   dense_precision, sparse_precision, hybrid_precision,
                   dense_mrr, sparse_mrr, hybrid_mrr,
                   llm_time, retrieval_time, total_time, timestamp
                FROM history_v2 WHERE session_id = ? ORDER BY id DESC LIMIT ?""", (session_id, limit)
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


def summarize_from_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    metrics: dict[str, Any] = {
        "query_expansion": {"hit_total": 0.0, "recall_total": 0.0, "precision_total": 0.0, "mrr_total": 0.0,
                            "llm_time_total": 0.0, "retrieval_time_total": 0.0, "total_time_total": 0.0, "count": 0.0},
    }
    for r in rows:
        hit = r.get("hybrid_hit")
        recall = r.get("hybrid_recall")
        precision = r.get("hybrid_precision")
        mrr = r.get("hybrid_mrr")
        if hit is None or recall is None or precision is None or mrr is None:
            continue
        s = metrics["query_expansion"]
        s["hit_total"] += float(hit)
        s["recall_total"] += float(recall)
        s["precision_total"] += float(precision)
        s["mrr_total"] += float(mrr)
        s["llm_time_total"] += float(r.get("llm_time", 0.0) or 0.0)
        s["retrieval_time_total"] += float(r.get("retrieval_time", 0.0) or 0.0)
        s["total_time_total"] += float(r.get("total_time", 0.0) or 0.0)
        s["count"] += 1.0
    summary: dict[str, dict[str, float]] = {}
    for name, stat in metrics.items():
        c = stat["count"]
        if c <= 0:
            summary[name] = {"hit": 0.0, "recall": 0.0, "precision": 0.0, "mrr": 0.0,
                             "avg_llm_time": 0.0, "avg_retrieval_time": 0.0, "avg_total_time": 0.0}
        else:
            summary[name] = {"hit": stat["hit_total"] / c, "recall": stat["recall_total"] / c,
                             "precision": stat["precision_total"] / c, "mrr": stat["mrr_total"] / c,
                             "avg_llm_time": stat["llm_time_total"] / c,
                             "avg_retrieval_time": stat["retrieval_time_total"] / c,
                             "avg_total_time": stat["total_time_total"] / c}
    return summary


def format_duration(seconds: float | None) -> str:
    value = float(seconds or 0.0)
    if value < 0.001:
        return f"{value * 1_000_000:.0f}us"
    if value < 1.0:
        return f"{value * 1000:.3f}ms"
    return f"{value:.3f}s"


def _view_for_method(results: list[dict[str, Any]], ground_truth_ranked: list[str]) -> list[dict[str, Any]]:
    gt = set(ground_truth_ranked)
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(results[:TOP_K]):
        cid = item.get("control_id", "")
        title = item.get("title", "")
        score = float(item.get("score", 0.0))
        rows.append({"control_id": cid, "text": f"{cid} - {title} ({score:.3f})",
                      "is_match": cid in gt, "is_top1": idx == 0})
    return rows


def _empty_metrics() -> dict[str, float | None]:
    return {"hit": None, "recall": None, "precision": None, "mrr": None}


def _process_retrieval_only(
    query_id: str | None, query: str, ground_truth_ranked: list[str],
    k: int = TOP_K, method_order: list[str] | None = None,
    session_id: int | None = None, single_method: bool = False,
) -> dict[str, Any]:
    expected_count = 1 if single_method else None
    order = normalize_method_order(method_order, expected_count=expected_count)
    if single_method and len(order) != 1:
        raise Exception("Single-method evaluation expected exactly one method.")
    v2_result = pipeline.run(query=query, k=k)
    active_methods = set(order)
    executed_method = order[0] if len(order) == 1 else None
    dense_top = compact_results(v2_result.get("dense_results", []), "dense_score", k=k) if "dense" in active_methods else []
    sparse_top = compact_results(v2_result.get("sparse_results", []), "sparse_score", k=k) if "sparse" in active_methods else []
    hybrid_top = compact_results(v2_result.get("hybrid_results", []), "hybrid_score", k=k) if "hybrid" in active_methods else []
    dense_ids = [x["control_id"] for x in dense_top]
    sparse_ids = [x["control_id"] for x in sparse_top]
    hybrid_ids = [x["control_id"] for x in hybrid_top]
    dense_metrics = compute_metrics(dense_ids, ground_truth_ranked, k=k) if "dense" in active_methods else _empty_metrics()
    sparse_metrics = compute_metrics(sparse_ids, ground_truth_ranked, k=k) if "sparse" in active_methods else _empty_metrics()
    hybrid_metrics = compute_metrics(hybrid_ids, ground_truth_ranked, k=k) if "hybrid" in active_methods else _empty_metrics()
    timings = v2_result.get("timings", {"llm_time": 0.0, "retrieval_time": 0.0, "total_time": 0.0})
    save_history_row(
        session_id=session_id, method_name=executed_method, query_id=query_id,
        original_query=query, expanded_query=v2_result["expanded_query"],
        dense_results=dense_top, sparse_results=sparse_top, hybrid_results=hybrid_top,
        ground_truth_ranked=ground_truth_ranked,
        dense_metrics=dense_metrics, sparse_metrics=sparse_metrics, hybrid_metrics=hybrid_metrics,
        timings=timings, method_order=order,
    )
    return {
        "query_id": query_id, "original_query": query, "expanded_query": v2_result["expanded_query"],
        "ground_truth_ranked": ground_truth_ranked,
        "dense_results": dense_top, "sparse_results": sparse_top, "hybrid_results": hybrid_top,
        "metrics": {"dense": dense_metrics, "sparse": sparse_metrics, "hybrid": hybrid_metrics},
        "timings": timings, "method_order": order, "method_name": executed_method, "session_id": session_id,
    }


def _run_bulk_in_background(payload: list[dict[str, Any]], method_order: list[str], session_id: int, single_method: bool) -> None:
    global BULK_THREAD
    try:
        total = len(payload)
        reset_progress(total, session_id=session_id, method_order=method_order)
        for idx, item in enumerate(payload, start=1):
            if not isinstance(item, dict):
                set_progress(idx - 1, total, "invalid item format", False, "Each item must be an object")
                return
            query_id = item.get("query_id")
            query_text = str(item.get("query", "")).strip()
            gt_ranked = item.get("ground_truth_ranked") or item.get("ground_truth", [])
            if not query_text:
                set_progress(idx - 1, total, "missing query", False, "Each item requires a non-empty 'query'")
                return
            if not isinstance(gt_ranked, list):
                set_progress(idx - 1, total, "invalid ground_truth_ranked", False, "ground_truth_ranked must be a list")
                return
            set_progress(idx - 1, total, f"processing query {idx}/{total}", True)
            processed = _process_retrieval_only(
                query_id=query_id, query=query_text, ground_truth_ranked=gt_ranked,
                k=TOP_K, method_order=method_order, session_id=session_id, single_method=single_method,
            )
            with PROGRESS_LOCK:
                PROGRESS_STATE["bulk_results"].append(processed)
            set_progress(idx, total, f"processed query {idx}/{total}", True)
        set_progress(total, total, "completed", False)
    except Exception as exc:
        import traceback
        set_progress(PROGRESS_STATE["current"], PROGRESS_STATE["total"], f"error: {exc}", False, str(exc) + "\n" + traceback.format_exc())
    finally:
        BULK_THREAD = None


INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V2 Query Expansion - Research Dashboard</title>
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
    .expand-badge { display: inline-block; background: #e3f2fd; color: #1565c0; border-radius: 12px; padding: 2px 10px; font-size: 11px; margin-left: 8px; }
  </style>
</head>
<body>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <h2>RAG V2 - Query Expansion Pipeline</h2>
    <div><span class="expand-badge">Query Expansion Active</span></div>
  </div>

  <div class="section">
    <h3>Single Query</h3>
    <textarea id="query" placeholder="Masukkan query..."></textarea>
    <textarea id="gtSingle" placeholder='Ground truth ranked (JSON array), contoh: ["A.5.11"]'></textarea>
    <div class="actions">
      <button onclick="runSingle()">Run Query (V2)</button>
      <a class="btn" href="/history/v2" target="_blank">Open V2 History</a>
    </div>
  </div>

  <div class="section">
    <h3>Bulk Input</h3>
    <textarea id="bulkInput" placeholder='[{"query_id":"Q1","query":"...","ground_truth_ranked":["A.5.18","A.5.16","A.5.15"]}]'></textarea>
    <div class="inline-options">
      <span><b>Session:</b></span>
      <label><input type="radio" name="sessionMode" value="new"> Start New Session</label>
      <label><input type="radio" name="sessionMode" value="continue" checked> Continue Last Session</label>
      <span id="sessionInfo" class="small">Current Session: -</span>
    </div>
    <div class="actions">
      <button id="bulkBtn" onclick="runBulk()">Run Bulk Evaluation (Query Expansion)</button>
    </div>
    <div id="progressWrap"><div id="progressBar"></div></div>
    <div id="progressText">Progress: 0% (Idle)</div>
    <div id="bulkResults"></div>
  </div>

  <div id="status"></div>

  <div class="section summary">
    <div><b>Expanded Query:</b> <span id="expandedQueryDisplay" class="small">-</span></div>
    <div><b>Top Hybrid:</b> <span id="topControl">-</span></div>
    <div><b>Answer:</b></div>
    <pre id="answerBox" class="mono small" style="max-height:220px;overflow:auto;">-</pre>
  </div>

  <div class="section"><h3>Dense Results</h3><div id="denseTable"></div></div>
  <div class="section"><h3>Sparse Results</h3><div id="sparseTable"></div></div>
  <div class="section"><h3>Hybrid Results</h3><div id="hybridTable"></div></div>

  <div id="modalOverlay" onclick="closeModal()">
    <div id="modalBox" onclick="event.stopPropagation()">
      <button id="modalClose" onclick="closeModal()">x</button>
      <h3 id="modalTitle">Control Detail</h3>
      <p><b>Objective</b></p><p id="modalObjective"></p>
      <p><b>Description</b></p><p id="modalDescription"></p>
    </div>
  </div>

  <script>
    function fmtScore(v) { return Number(v || 0).toFixed(3); }
    function fmtTime(v) {
      const n = Number(v || 0);
      if (n < 0.001) return (n * 1_000_000).toFixed(0) + 'us';
      if (n < 1) return (n * 1000).toFixed(3) + 'ms';
      return n.toFixed(3) + 's';
    }
    function openModal(item) {
      document.getElementById('modalTitle').textContent = item.control_id + ' - ' + item.title;
      document.getElementById('modalObjective').textContent = item.objective || '-';
      document.getElementById('modalDescription').textContent = item.description || '-';
      document.getElementById('modalOverlay').style.display = 'block';
    }
    function closeModal() { document.getElementById('modalOverlay').style.display = 'none'; }

    function renderTable(targetId, rows) {
      const target = document.getElementById(targetId);
      if (!rows || rows.length === 0) { target.innerHTML = '<div class="small">No results.</div>'; return; }
      let html = '';
      for (let i = 0; i < rows.length; i++) {
        const r = rows[i];
        html += '<tr class="data-row' + (i===0 ? ' top-row' : '') + '" data-idx="' + i + '">'
             + '<td>' + r.control_id + ' - ' + r.title + '</td>'
             + '<td class="mono">' + fmtScore(r.score || 0) + '</td></tr>';
      }
      target.innerHTML = '<table><thead><tr><th>Control</th><th>Score</th></tr></thead><tbody>' + html + '</tbody></table>';
      const tbody = target.querySelector('tbody');
      if (tbody) {
        tbody.querySelectorAll('tr.data-row').forEach(function(tr) {
          tr.addEventListener('click', function() {
            openModal(rows[Number(tr.getAttribute('data-idx'))]);
          });
        });
      }
    }

    function renderBulkResults(results) {
      const container = document.getElementById('bulkResults');
      if (!results || results.length === 0) {
        container.innerHTML = '<div class="small">No bulk results yet.</div>';
        return;
      }
      let html = '';
      for (let idx = 0; idx < results.length; idx++) {
        const r = results[idx];
        const denseHtml = (r.dense_results || []).map(function(item, i) {
          return '<tr class="' + (i===0 ? 'top-row ' : '') + 'data-row" data-idx="' + i + '"><td>' + item.control_id + '</td><td class="mono">' + fmtScore(item.score) + '</td></tr>';
        }).join('');
        const sparseHtml = (r.sparse_results || []).map(function(item, i) {
          return '<tr class="' + (i===0 ? 'top-row ' : '') + 'data-row" data-idx="' + i + '"><td>' + item.control_id + '</td><td class="mono">' + fmtScore(item.score) + '</td></tr>';
        }).join('');
        const hybridHtml = (r.hybrid_results || []).map(function(item, i) {
          return '<tr class="' + (i===0 ? 'top-row ' : '') + 'data-row" data-idx="' + i + '"><td>' + item.control_id + '</td><td class="mono">' + fmtScore(item.score) + '</td></tr>';
        }).join('');
        html += '<div class="bulk-item">'
             + '<h4>' + (r.query_id || 'Q' + (idx+1)) + ': ' + (r.original_query || '') + '</h4>'
             + '<div class="query-meta"><b>Expanded:</b> ' + (r.expanded_query || '-') + ' | '
             + 'GT: [' + (r.ground_truth_ranked || []).join(', ') + '] | '
             + 'Dense H:' + fmtScore(r.metrics?.dense?.hit) + ' R:' + fmtScore(r.metrics?.dense?.recall) + ' MRR:' + fmtScore(r.metrics?.dense?.mrr) + ' | '
             + 'Sparse H:' + fmtScore(r.metrics?.sparse?.hit) + ' R:' + fmtScore(r.metrics?.sparse?.recall) + ' MRR:' + fmtScore(r.metrics?.sparse?.mrr) + ' | '
             + 'Hybrid H:' + fmtScore(r.metrics?.hybrid?.hit) + ' R:' + fmtScore(r.metrics?.hybrid?.recall) + ' MRR:' + fmtScore(r.metrics?.hybrid?.mrr) + ' | '
             + 'LLM Time: ' + fmtTime(r.timings?.llm_time) + ' | '
             + 'Retrieval: ' + fmtTime(r.timings?.retrieval_time) + ' | '
             + 'Total: ' + fmtTime(r.timings?.total_time)
             + '</div>'
             + '<div class="result-grid">'
             + '<div class="result-col"><h5>Dense</h5><table><thead><tr><th>ID</th><th>Score</th></tr></thead><tbody>' + denseHtml + '</tbody></table></div>'
             + '<div class="result-col"><h5>Sparse</h5><table><thead><tr><th>ID</th><th>Score</th></tr></thead><tbody>' + sparseHtml + '</tbody></table></div>'
             + '<div class="result-col"><h5>Hybrid</h5><table><thead><tr><th>ID</th><th>Score</th></tr></thead><tbody>' + hybridHtml + '</tbody></table></div>'
             + '</div></div>';
      }
      container.innerHTML = html;
    }

    let pollInterval = null;
    function setBulkButtonsDisabled(disabled) {
      const el = document.getElementById('bulkBtn');
      if (el) el.disabled = disabled;
    }
    async function refreshSessionInfo() {
      try {
        const res = await fetch('/v2/session-info');
        const data = await res.json();
        document.getElementById('sessionInfo').textContent = 'Current Session: ' + (data.latest_session_id == null ? '-' : data.latest_session_id);
      } catch (_) {}
    }
    async function pollProgress() {
      try {
        const res = await fetch('/v2/progress');
        const p = await res.json();
        document.getElementById('progressBar').style.width = p.percentage + '%';
        document.getElementById('progressText').textContent = 'Session ' + (p.session_id == null ? '-' : p.session_id)
          + ' | Processing Query ' + p.current + ' / ' + p.total + '... (' + p.percentage + '%) - ' + p.status;
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
          document.getElementById('status').textContent = 'Bulk completed. Session ' + (p.session_id || '-') + '. Processed: ' + p.current + ' queries.';
          setBulkButtonsDisabled(false);
          refreshSessionInfo();
        }
      } catch (e) { console.error('Poll error:', e); }
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
        const res = await fetch('/v2/query', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ query: query, ground_truth_ranked: gt })
        });
        const data = await res.json();
        if (!res.ok) { status.textContent = 'Error: ' + (data.error || 'Unknown'); return; }
        const top = (data.hybrid_results && data.hybrid_results[0]) || null;
        document.getElementById('expandedQueryDisplay').textContent = data.expanded_query || '-';
        document.getElementById('topControl').textContent = top ? top.control_id + ' - ' + top.title : '-';
        document.getElementById('answerBox').textContent = typeof data.answer === 'string' ? data.answer : JSON.stringify(data.answer, null, 2);
        renderTable('denseTable', data.dense_results || []);
        renderTable('sparseTable', data.sparse_results || []);
        renderTable('hybridTable', data.hybrid_results || []);
        status.textContent = 'Done.';
      } catch (e) {
        status.textContent = 'Error: ' + e.message;
      }
    }

    async function runBulk() {
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
        const res = await fetch('/v2/bulk-query', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ items: payload, method_order: ['dense','sparse','hybrid'], session_mode: sessionMode })
        });
        const data = await res.json();
        if (!res.ok) { status.textContent = 'Bulk error: ' + (data.error || 'Unknown'); setBulkButtonsDisabled(false); return; }
        status.textContent = 'Bulk started. Session ' + (data.session_id == null ? '-' : data.session_id) + '.';
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
  <title>RAG V2 - Query Expansion History</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 16px; color: #222; }
    .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; table-layout: fixed; }
    th, td { border: 1px solid #ddd; padding: 7px; text-align: left; font-size: 12px; vertical-align: top; word-wrap: break-word; }
    th { background: #f3f3f3; }
    .summary { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px; padding: 10px; margin-bottom: 12px; }
    .query-cell { cursor: pointer; color: #1565c0; }
    .query-cell:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="header-actions">
    <h2>V2 Query Expansion History - Session {{ session_id }}</h2>
    <div>
      <a class="btn" href="/v2">Back to V2 Dashboard</a>
      <a class="btn" href="/history/v2">All V2 Sessions</a>
      <button class="btn-reset" onclick="resetHistory()">Reset V2 History</button>
    </div>
  </div>
  <div class="summary">
    <h3>Overall Performance</h3>
    <table>
      <thead><tr><th>Method</th><th>Hit@3</th><th>Recall@3</th><th>Precision@3</th><th>MRR</th><th colspan="3">AVG Time Process</th></tr>
      <tr><th></th><th></th><th></th><th></th><th></th><th>LLM Time</th><th>Retrieval Time</th><th>Total Time</th></tr></thead>
      <tbody>
        {% set s = summary["query_expansion"] %}
        <tr>
          <td><b>Query Expansion</b></td>
          <td>{{ "%.3f"|format(s["hit"]) }}</td>
          <td>{{ "%.3f"|format(s["recall"]) }}</td>
          <td>{{ "%.3f"|format(s["precision"]) }}</td>
          <td>{{ "%.3f"|format(s["mrr"]) }}</td>
          <td>{{ format_duration(s["avg_llm_time"]) }}</td>
          <td>{{ format_duration(s["avg_retrieval_time"]) }}</td>
          <td>{{ format_duration(s["avg_total_time"]) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <table>
    <thead><tr><th>ID</th><th>Original Query</th><th>Query Expansion</th><th>Hybrid</th><th>GT</th><th>Metrics</th><th>Time</th></tr></thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td><b>{{ r.query_id or "-" }}</b></td>
        <td><div class="query-cell" onclick="openQueryModal({{ loop.index0 }}, 'original')">{{ r.original_query[:80] }}{% if r.original_query|length > 80 %}...{% endif %}</div></td>
        <td><div class="query-cell" onclick="openQueryModal({{ loop.index0 }}, 'expanded')">{{ r.expanded_query[:80] }}{% if r.expanded_query|length > 80 %}...{% endif %}</div></td>
        <td>{% for item in r.hybrid_view %}<div class="item {% if item.is_top1 %}top1{% endif %} {% if item.is_match %}correct{% else %}wrong{% endif %}" data-control-id="{{ item.control_id }}">{{ item.text }}</div>{% endfor %}</td>
        <td>{% for gt in r.ground_truth %}<span class="gt-tag">{{ gt }}</span>{% endfor %}</td>
        <td class="mono">H:{{ "%.2f"|format(r.hybrid_hit or 0) }} R:{{ "%.2f"|format(r.hybrid_recall or 0) }}<br>P:{{ "%.2f"|format(r.hybrid_precision or 0) }} MRR:{{ "%.3f"|format(r.hybrid_mrr or 0) }}</td>
        <td class="mono">LLM: {{ format_duration(r.llm_time or 0) }}<br>Retrieval: {{ format_duration(r.retrieval_time or 0) }}<br>Total: {{ format_duration(r.total_time or 0) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <div id="modalOverlay" style="display:none;position:fixed;z-index:20;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.45);" onclick="closeQueryModal()">
    <div style="background:#fff;width:min(800px,90%);margin:6% auto;border-radius:8px;padding:16px;border:1px solid #ddd;" onclick="event.stopPropagation()">
      <button style="float:right;border:0;background:transparent;font-size:20px;cursor:pointer;" onclick="closeQueryModal()">x</button>
      <h3 id="queryModalTitle">Query</h3>
      <pre id="queryModalContent" class="mono" style="white-space:pre-wrap;word-wrap:break-word;max-height:400px;overflow-y:auto;"></pre>
    </div>
  </div>
  <div id="controlModalOverlay" style="display:none;position:fixed;z-index:20;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.45);" onclick="closeControlModal()">
    <div style="background:#fff;width:min(800px,90%);margin:6% auto;border-radius:8px;padding:16px;border:1px solid #ddd;" onclick="event.stopPropagation()">
      <button style="float:right;border:0;background:transparent;font-size:20px;cursor:pointer;" onclick="closeControlModal()">x</button>
      <h3 id="controlModalTitle">Control Detail</h3>
      <p><b>Objective</b></p><p id="controlModalObjective"></p>
      <p><b>Description</b></p><p id="controlModalDescription"></p>
    </div>
  </div>
  <script>
    const controlCatalog = {{ control_catalog|safe }};
    const rowsData = {{ rows_data|safe }};
    function openQueryModal(idx, type) {
      const r = rowsData[idx];
      const title = type === "original" ? "Original Query" : "Expanded Query";
      const content = type === "original" ? r.original_query : r.expanded_query;
      document.getElementById("queryModalTitle").textContent = title;
      document.getElementById("queryModalContent").textContent = content || "-";
      document.getElementById("modalOverlay").style.display = "block";
    }
    function closeQueryModal() { document.getElementById("modalOverlay").style.display = "none"; }
    function openControlModal(cid) {
      const info = controlCatalog[cid];
      if (!info) return;
      document.getElementById("controlModalTitle").textContent = cid + " - " + info.title;
      document.getElementById("controlModalObjective").textContent = info.objective || "-";
      document.getElementById("controlModalDescription").textContent = info.description || "-";
      document.getElementById("controlModalOverlay").style.display = "block";
    }
    function closeControlModal() { document.getElementById("controlModalOverlay").style.display = "none"; }
    document.querySelectorAll(".item[data-control-id]").forEach(function(el) {
      el.addEventListener("click", function() { openControlModal(el.getAttribute("data-control-id")); });
    });
    async function resetHistory() {
      if (!confirm("Are you sure?")) return;
      const res = await fetch("/history/v2", { method: "DELETE" });
      if (res.ok) window.location.reload();
      else { const d = await res.json(); alert("Failed: " + (d.error || "Unknown")); }
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
  <title>RAG V2 - Sessions</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; color: #222; }
    .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    a.btn { padding: 8px 14px; border: 1px solid #bbb; background: #f7f7f7; border-radius: 6px; text-decoration: none; color: #222; }
    .session-list { display: flex; flex-direction: column; gap: 8px; max-width: 700px; }
    .session-item { display: block; padding: 12px; border: 1px solid #ddd; border-radius: 8px; text-decoration: none; color: #222; background: #fafafa; }
    .session-item:hover { background: #f1f7ff; border-color: #aac7ff; }
    .btn-reset { padding: 8px 14px; border: 1px solid #d73a49; background: #fff; border-radius: 6px; cursor: pointer; color: #d73a49; }
  </style>
</head>
<body>
  <div class="header-actions">
    <h2>V2 Query Expansion - History Sessions</h2>
    <div>
      <a class="btn" href="/v2">Back to V2 Dashboard</a>
      <button class="btn-reset" onclick="resetHistory()">Reset V2 History</button>
    </div>
  </div>
  {% if sessions %}
  <div class="session-list">
    {% for s in sessions %}
    <a class="session-item" href="/history/v2/{{ s.session_id }}">
      <div><b>Session {{ s.session_id }}</b> ({{ s.row_count }} rows)</div>
      <div class="small">{{ s.started_at }} - {{ s.finished_at }}</div>
    </a>
    {% endfor %}
  </div>
  {% else %}
  <div class="small">No V2 sessioned records yet.</div>
  {% endif %}
  <script>
    async function resetHistory() {
      if (!confirm("Are you sure?")) return;
      const res = await fetch("/history/v2", { method: "DELETE" });
      if (res.ok) window.location.reload();
      else { const d = await res.json(); alert("Failed: " + (d.error || "Unknown")); }
    }
  </script>
</body>
</html>
"""


# === FLASK ROUTES ===

@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


@app.get("/v2")
def v2_index():
    return render_template_string(INDEX_HTML)


@app.get("/v2/progress")
def v2_progress():
    with PROGRESS_LOCK:
        data = dict(PROGRESS_STATE)
    return jsonify(data)


@app.post("/v2/query")
def v2_query():
    body = request.get_json(silent=True) or {}
    query_text = str(body.get("query", "")).strip()
    query_id = body.get("query_id")
    gt_ranked = body.get("ground_truth_ranked") or body.get("ground_truth", [])
    if not query_text:
        return jsonify({"error": "query is required"}), 400
    if not isinstance(gt_ranked, list):
        return jsonify({"error": "ground_truth_ranked must be a list"}), 400
    k = int(body.get("k", TOP_K))
    method_order = body.get("method_order", DEFAULT_METHOD_ORDER)
    single_method = bool(body.get("single_method", False))
    session_id = body.get("session_id")
    if session_id is not None:
        try: session_id = int(session_id)
        except (TypeError, ValueError): return jsonify({"error": "session_id must be integer"}), 400
    try:
        method_order = normalize_method_order(method_order, expected_count=1 if single_method else None)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    try:
        processed = _process_retrieval_only(
            query_id=query_id, query=query_text, ground_truth_ranked=gt_ranked,
            k=k, method_order=method_order, session_id=session_id, single_method=single_method,
        )
        v2_result = pipeline.run(query=query_text, k=k)
        response = {
            "query_id": query_id,
            "original_query": query_text,
            "expanded_query": v2_result["expanded_query"],
            "dense_results": processed["dense_results"],
            "sparse_results": processed["sparse_results"],
            "hybrid_results": processed["hybrid_results"],
            "ground_truth_ranked": gt_ranked,
            "metrics": processed["metrics"],
            "timings": processed["timings"],
            "method_order": processed["method_order"],
            "method_name": processed["method_name"],
            "session_id": processed["session_id"],
            "answer": v2_result.get("answer"),
            "llm_model": v2_result.get("llm_model"),
            "llm_error": v2_result.get("llm_error"),
            "fusion": {"method": "weighted_sum", "dense_weight": 0.6, "sparse_weight": 0.4},
        }
        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/v2/bulk-query")
def v2_bulk_query():
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
    return jsonify({"message": "Bulk processing started", "status": "started", "session_id": session_id, "method_order": order, "single_method": single_method})


@app.get("/v2/session-info")
def v2_session_info():
    latest = get_latest_session_id()
    return jsonify({"latest_session_id": latest})


@app.get("/history/v2")
def v2_history_index():
    sessions = get_session_summaries()
    if request.args.get("format") == "json":
        return jsonify({"sessions": sessions})
    return render_template_string(HISTORY_INDEX_HTML, sessions=sessions)


@app.get("/history/v2/<int:session_id>")
def v2_history_by_session(session_id: int):
    rows = get_history_rows(session_id=session_id)
    summary = summarize_from_rows(rows)
    for row in rows:
        gt = row.get("ground_truth", [])
        row["hybrid_view"] = _view_for_method(row.get("hybrid_results", []), gt)
    if request.args.get("format") == "json":
        return jsonify({"session_id": session_id, "rows": rows, "summary": summary})
    import html as html_mod
    rows_json = json.dumps([{
        "original_query": r.get("original_query", ""),
        "expanded_query": r.get("expanded_query", ""),
    } for r in rows], ensure_ascii=False)
    return render_template_string(
        HISTORY_HTML,
        session_id=session_id,
        rows=rows,
        summary=summary,
        control_catalog=json.dumps(CONTROL_CATALOG, ensure_ascii=False),
        format_duration=format_duration,
        rows_data=rows_json,
    )


@app.delete("/history/v2")
def v2_reset_history():
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM history_v2")
            conn.commit()
        return jsonify({"message": "V2 history cleared successfully"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=True, threaded=True)
