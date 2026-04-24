import json
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

DB_PATH = PROJECT_ROOT / "rag_history.db"
TOP_K = 3
HISTORY_LIMIT = 300

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


def reset_progress(total: int) -> None:
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
        ]:
            if not _column_exists(conn, "history", col_name):
                conn.execute(f"ALTER TABLE history ADD COLUMN {col_name} {col_type}")

        conn.commit()


def load_control_catalog() -> dict[str, dict[str, str]]:
    controls_path = PROJECT_ROOT / "data" / "iso_controls.json"
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
) -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO history (
                query_id, query, dense_results, sparse_results, hybrid_results, ground_truth,
                dense_hit, sparse_hit, hybrid_hit,
                dense_recall, sparse_recall, hybrid_recall,
                dense_precision, sparse_precision, hybrid_precision,
                dense_mrr, sparse_mrr, hybrid_mrr,
                dense_time, sparse_time, hybrid_time, total_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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


def get_history_rows(limit: int = HISTORY_LIMIT) -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id, query_id, query, dense_results, sparse_results, hybrid_results, ground_truth,
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

    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["dense_results"] = _safe_json_list(item.get("dense_results"))
        item["sparse_results"] = _safe_json_list(item.get("sparse_results"))
        item["hybrid_results"] = _safe_json_list(item.get("hybrid_results"))
        item["ground_truth"] = _safe_json_list(item.get("ground_truth"))
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


def _process_retrieval_only(query_id: str | None, query: str, ground_truth_ranked: list[str], k: int = TOP_K) -> dict[str, Any]:
    retrieval = pipeline.retriever.retrieve(query=query, k=k)

    dense_top = compact_results(retrieval.get("dense_results", []), "dense_score", k=k)
    sparse_top = compact_results(retrieval.get("sparse_results", []), "sparse_score", k=k)
    hybrid_top = compact_results(retrieval.get("hybrid_results", []), "hybrid_score", k=k)

    dense_ids = [x["control_id"] for x in dense_top]
    sparse_ids = [x["control_id"] for x in sparse_top]
    hybrid_ids = [x["control_id"] for x in hybrid_top]

    dense_metrics = compute_metrics(dense_ids, ground_truth_ranked, k=k)
    sparse_metrics = compute_metrics(sparse_ids, ground_truth_ranked, k=k)
    hybrid_metrics = compute_metrics(hybrid_ids, ground_truth_ranked, k=k)
    timings = retrieval.get("timings", {"dense_time": 0.0, "sparse_time": 0.0, "hybrid_time": 0.0, "total_time": 0.0})

    save_history_row(
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
    }


def _run_bulk_in_background(payload: list[dict[str, Any]]) -> None:
    global BULK_THREAD
    try:
        total = len(payload)
        reset_progress(total)
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

            processed = _process_retrieval_only(query_id=query_id, query=query_text, ground_truth_ranked=gt_ranked, k=TOP_K)
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
    <h3>Bulk Input</h3>
    <textarea id="bulkInput" placeholder='[{"query_id":"Q1","query":"...","ground_truth_ranked":["A.5.18","A.5.16","A.5.15"]}]'></textarea>
    <div class="actions">
      <button id="bulkBtn" onclick="runBulk()">Run Bulk Evaluation</button>
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
    async function pollProgress() {
      try {
        const res = await fetch('/progress');
        const p = await res.json();
        document.getElementById('progressBar').style.width = `${p.percentage}%`;
        document.getElementById('progressText').textContent = `Processing Query ${p.current} / ${p.total}... (${p.percentage}%) - ${p.status}`;
        if (p.bulk_results && p.bulk_results.length > 0) {
          renderBulkResults(p.bulk_results);
        }
        if (p.error) {
          document.getElementById('status').textContent = 'Error: ' + p.error;
          clearInterval(pollInterval);
          document.getElementById('bulkBtn').disabled = false;
          return;
        }
        if (!p.running && p.current > 0) {
          clearInterval(pollInterval);
          document.getElementById('status').textContent = `Bulk completed. Processed: ${p.current} queries.`;
          document.getElementById('bulkBtn').disabled = false;
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

    async function runBulk() {
      const status = document.getElementById('status');
      const raw = document.getElementById('bulkInput').value.trim();
      if (!raw) { status.textContent = 'Bulk input wajib diisi.'; return; }
      let payload = null;
      try { payload = JSON.parse(raw); } catch { status.textContent = 'JSON bulk tidak valid.'; return; }
      if (!Array.isArray(payload)) { status.textContent = 'Payload bulk harus array.'; return; }

      status.textContent = 'Starting bulk evaluation...';
      document.getElementById('bulkBtn').disabled = true;
      document.getElementById('bulkResults').innerHTML = '';

      try {
        const res = await fetch('/bulk-query', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          status.textContent = 'Bulk error: ' + (data.error || 'Unknown');
          document.getElementById('bulkBtn').disabled = false;
          return;
        }
        pollInterval = setInterval(pollProgress, 500);
      } catch (e) {
        status.textContent = 'Bulk error: ' + e.message;
        document.getElementById('bulkBtn').disabled = false;
      }
    }
  </script>
</body>
</html>
"""


HISTORY_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>RAG V1 - History Evaluation</title>
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
    <h2>History Evaluation</h2>
    <div>
      <a class="btn" href="/">← Back to Dashboard</a>
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

    try:
        processed = _process_retrieval_only(query_id=query_id, query=query_text, ground_truth_ranked=gt_ranked, k=k)
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
            "answer": llm_result.get("answer"),
            "llm_model": llm_result.get("llm_model"),
            "llm_error": llm_result.get("llm_error"),
            "fusion": {"method": "weighted_sum", "dense_weight": 0.6, "sparse_weight": 0.4},
        }
        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/bulk-query")
def bulk_query():
    global BULK_THREAD
    payload = request.get_json(silent=True)
    if not isinstance(payload, list):
        return jsonify({"error": "Payload must be a JSON array"}), 400

    if PROGRESS_STATE["running"]:
        return jsonify({"error": "Another bulk operation is already running"}), 400

    BULK_THREAD = threading.Thread(target=_run_bulk_in_background, args=(payload,))
    BULK_THREAD.start()

    return jsonify({"message": "Bulk processing started", "status": "started"})


@app.get("/history")
def history():
    if request.method == "DELETE":
        try:
            with get_db_connection() as conn:
                conn.execute("DELETE FROM history")
                conn.commit()
            return jsonify({"message": "History cleared successfully"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    rows = get_history_rows()
    summary = summarize_from_rows(rows)
    best_method = best_method_by_mrr(summary)

    for row in rows:
        gt = row.get("ground_truth", [])
        row["dense_view"] = _view_for_method(row.get("dense_results", []), gt)
        row["sparse_view"] = _view_for_method(row.get("sparse_results", []), gt)
        row["hybrid_view"] = _view_for_method(row.get("hybrid_results", []), gt)

    if request.args.get("format") == "json":
        return jsonify({"rows": rows, "summary": summary, "best_method": best_method})

    return render_template_string(
        HISTORY_HTML,
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


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=True, threaded=True)
