# llm/llm_wrapper.py
# Wrapper for Ollama local LLM inference (CybersecurityRiskAnalyst 8B Q4_0)

import json
import re
import time
import logging
import requests

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"
TEMPERATURE = 0.0
REQUEST_TIMEOUT = 600

REQUIRED_KEYS = {"control_id", "applicable", "implementation_status", "justification", "recommendation"}
VALID_APPLICABLE = {"Yes", "No"}
VALID_STATUS = {"Implemented", "Partially Implemented", "Not Implemented"}


def call_ollama(prompt: str) -> str:
    """
    Send a prompt to Ollama and return the raw text response.

    Args:
        prompt: Full prompt string.

    Returns:
        Raw response text from the LLM.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "temperature": TEMPERATURE,
        "stream": False,
        "options": {
            "num_predict": 256,
        },
    }

    start = time.time()
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.ConnectionError:
        raise ConnectionError(
            f"Tidak dapat terhubung ke Ollama di {OLLAMA_URL}. "
            "Pastikan Ollama sedang berjalan (ollama serve)."
        )
    except requests.Timeout:
        raise TimeoutError(f"Ollama timeout setelah {REQUEST_TIMEOUT} detik.")

    elapsed = time.time() - start
    result = resp.json()
    response_text = result.get("response", "")

    logger.info(f"Ollama response time: {elapsed:.2f}s")
    return response_text


def extract_json(text: str) -> dict | None:
    """
    Extract JSON object from LLM response text.
    Tries multiple strategies to find valid JSON.
    """
    # Strategy 1: Try parsing the whole text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: Find JSON between curly braces
    match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find the largest {...} block (handles nested braces)
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    start = None

    return None


def validate_response(data: dict) -> dict:
    """
    Validate and normalize the LLM response to match expected schema.

    Returns validated dict or raises ValueError.
    """
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"Missing keys: {missing}")

    # Normalize control_id
    cid = str(data["control_id"]).strip()
    if not re.match(r'^A\.[5-8]\.\d+$', cid):
        raise ValueError(f"Invalid control_id format: {cid}")
    data["control_id"] = cid

    # Normalize applicable
    app = str(data["applicable"]).strip()
    if app not in VALID_APPLICABLE:
        raise ValueError(f"Invalid applicable: {app}")
    data["applicable"] = app

    # Normalize implementation_status
    status = str(data["implementation_status"]).strip()
    if status not in VALID_STATUS:
        # Try fuzzy matching
        status_lower = status.lower()
        if "partial" in status_lower:
            status = "Partially Implemented"
        elif "not" in status_lower:
            status = "Not Implemented"
        elif "implement" in status_lower:
            status = "Implemented"
        else:
            raise ValueError(f"Invalid implementation_status: {status}")
    data["implementation_status"] = status

    data["justification"] = str(data.get("justification", "")).strip()
    data["recommendation"] = str(data.get("recommendation", "")).strip()

    return data


def query_llm(prompt: str) -> dict:
    """
    Send prompt to Ollama, extract and validate JSON response.

    Args:
        prompt: Full prompt string.

    Returns:
        Validated dict with control_id, applicable, implementation_status,
        justification, recommendation.

    Raises:
        ValueError if response cannot be parsed or validated.
    """
    raw = call_ollama(prompt)
    logger.info(f"Raw LLM response:\n{raw}")

    data = extract_json(raw)
    if data is None:
        raise ValueError(f"Could not extract JSON from response:\n{raw}")

    return validate_response(data)


def query_llm_raw(prompt: str) -> tuple[dict | None, str, float]:
    """
    Like query_llm but returns (parsed_dict_or_None, raw_text, elapsed_seconds).
    Does not raise on parse failure or timeout — returns None instead.
    """
    start = time.time()
    try:
        raw = call_ollama(prompt)
    except (ConnectionError, TimeoutError) as e:
        elapsed = time.time() - start
        return None, f"ERROR: {e}", elapsed

    elapsed = time.time() - start

    data = extract_json(raw)
    if data is not None:
        try:
            data = validate_response(data)
        except ValueError:
            data = None

    return data, raw, elapsed
