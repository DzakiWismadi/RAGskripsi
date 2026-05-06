#!/usr/bin/env python
"""Test V2 imports"""
import sys
from pathlib import Path
import importlib.util

V2_ROOT = Path(r"D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2")
V1_ROOT = V2_ROOT.parent / "ragV1"

sys.path.insert(0, str(V2_ROOT))
sys.path.insert(1, str(V1_ROOT))

print(f"V2_ROOT: {V2_ROOT}")
print(f"V1_ROOT: {V1_ROOT}")
print(f"sys.path[0]: {sys.path[0]}")
print(f"sys.path[1]: {sys.path[1]}")

# Load query_expansion
print("\n=== Loading query_expansion ===")
qe_spec = importlib.util.spec_from_file_location("query_expansion", V2_ROOT / "query_expansion" / "query_expansion.py")
print(f"qe_spec: {qe_spec}")
qe_module = importlib.util.module_from_spec(qe_spec)
qe_spec.loader.exec_module(qe_module)
print(f"query_expansion function: {qe_module.query_expansion}")

# Load V2 pipeline
print("\n=== Loading rag_pipeline_v2 ===")
v2_spec = importlib.util.spec_from_file_location("rag_pipeline_v2", V2_ROOT / "pipeline" / "rag_pipeline_v2.py")
print(f"v2_spec: {v2_spec}")
v2_module = importlib.util.module_from_spec(v2_spec)
v2_spec.loader.exec_module(v2_module)
print(f"RAGPipelineV2 class: {v2_module.RAGPipelineV2}")

# Initialize pipeline
print("\n=== Initializing RAGPipelineV2 ===")
try:
    pipeline = v2_module.RAGPipelineV2(project_root=V2_ROOT)
    print(f"Pipeline created: {pipeline}")
    print(f"Retriever: {pipeline.retriever}")
    print("SUCCESS!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
