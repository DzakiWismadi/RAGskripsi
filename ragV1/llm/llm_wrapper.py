import json
import re
from typing import Any

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"
TEMPERATURE = 0.0
REQUEST_TIMEOUT = 120


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "temperature": TEMPERATURE,
        "stream": False,
        "options": {"num_predict": 256},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("response", "")).strip()


def extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    candidate = match.group(0)
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return None
    return None


def generate_answer(prompt: str) -> dict[str, Any]:
    raw = call_ollama(prompt)
    parsed = extract_json(raw)
    return {
        "model": MODEL_NAME,
        "raw_text": raw,
        "parsed_json": parsed,
    }

