import time
from pathlib import Path
from typing import Any

import requests

EXPAND_OLLAMA_URL = "http://localhost:11434/api/generate"
EXPAND_MODEL_NAME = "qwen2.5:3b"
EXPAND_TEMPERATURE = 0.0
EXPAND_TIMEOUT = 120


def _get_expand_prompt_path() -> Path:
    return Path(__file__).resolve().parents[2] / "ragV1" / "prompts" / "prompt_rewriting.txt"


def _load_expand_prompt_template() -> str:
    return _get_expand_prompt_path().read_text(encoding="utf-8").strip()


def build_expansion_prompt(query: str) -> str:
    template = _load_expand_prompt_template()
    return template.replace("{query}", query)


def call_ollama_expand(prompt: str) -> str:
    payload = {
        "model": EXPAND_MODEL_NAME,
        "prompt": prompt,
        "temperature": EXPAND_TEMPERATURE,
        "stream": False,
        "options": {"num_predict": 256},
    }
    resp = requests.post(EXPAND_OLLAMA_URL, json=payload, timeout=EXPAND_TIMEOUT)
    resp.raise_for_status()
    return str(resp.json().get("response", "")).strip()


def query_expansion(query: str) -> dict[str, Any]:
    prompt = build_expansion_prompt(query)

    start = time.perf_counter()
    try:
        raw = call_ollama_expand(prompt)
        llm_time = time.perf_counter() - start
        expanded = raw if raw else query
    except requests.RequestException:
        llm_time = time.perf_counter() - start
        expanded = query

    return {
        "original_query": query,
        "expanded_query": expanded,
        "llm_time": llm_time,
    }
