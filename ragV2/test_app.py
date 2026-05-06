#!/usr/bin/env python
"""Simple V2 Flask Test App"""
import sys
from pathlib import Path
import importlib.util
from flask import Flask, jsonify

V2_ROOT = Path(__file__).resolve().parents[1]
V1_ROOT = V2_ROOT.parent / "ragV1"

sys.path.insert(0, str(V2_ROOT))
sys.path.insert(1, str(V1_ROOT))

# Load modules explicitly
qe_spec = importlib.util.spec_from_file_location("query_expansion", V2_ROOT / "query_expansion" / "query_expansion.py")
qe_module = importlib.util.module_from_spec(qe_spec)
qe_spec.loader.exec_module(qe_module)

v2_spec = importlib.util.spec_from_file_location("rag_pipeline_v2", V2_ROOT / "pipeline" / "rag_pipeline_v2.py")
v2_module = importlib.util.module_from_spec(v2_spec)
v2_spec.loader.exec_module(v2_module)

RAGPipelineV2 = v2_module.RAGPipelineV2

app = Flask(__name__)
pipeline = RAGPipelineV2(project_root=V2_ROOT)

@app.get("/")
def index():
    return jsonify({
        "message": "RAG V2 Query Expansion System",
        "version": "2.0",
        "endpoints": ["/", "/v2", "/health"]
    })

@app.get("/v2")
def v2_index():
    return jsonify({
        "message": "RAG V2 Dashboard",
        "status": "operational"
    })

@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "pipeline": str(type(pipeline).__name__)
    })

if __name__ == "__main__":
    print("Starting RAG V2 Flask App...")
    print(f"Pipeline: {pipeline}")
    print(f"Retriever: {pipeline.retriever}")
    app.run(host="127.0.0.1", port=5001, debug=True)
