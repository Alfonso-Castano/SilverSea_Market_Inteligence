"""Smoke test for the local (Ollama) LLM backend added in feature 002-local-llm-backend.

This is the feature's evidence gate: it proves the local backend produces real,
schema-compliant JSON from an actual Ollama call — not a mock. It skips cleanly
(does not fail/error) whenever the local infrastructure isn't present on this
machine, since that's expected on most dev machines most of the time.

No Groq API calls happen anywhere in this file.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

from config.models import LOCAL_MODEL
import pipeline.analyst as analyst

SETUP_INSTRUCTIONS = (
    f"Local model '{LOCAL_MODEL}' is not registered in Ollama (checked via `ollama list`). "
    "To set it up: "
    "1) Download a Q6_K GGUF of Qwen3-32B from 'bartowski/Qwen3-32B-GGUF' on Hugging Face. "
    "2) Write a one-line Modelfile: `FROM ./Qwen3-32B-Q6_K.gguf`. "
    f"3) Register it: `ollama create {LOCAL_MODEL} -f Modelfile`."
)


def _extract_model_names(list_response):
    """Best-effort extraction of model tag names from ollama.list()'s response,
    tolerating both the newer object-based client shape and a plain dict shape."""
    models = getattr(list_response, "models", None)
    if models is None and isinstance(list_response, dict):
        models = list_response.get("models", [])
    models = models or []

    names = []
    for m in models:
        name = getattr(m, "model", None) or getattr(m, "name", None)
        if name is None and isinstance(m, dict):
            name = m.get("model") or m.get("name")
        if name:
            names.append(name)
    return names


def _check_local_backend_available():
    """Returns (available, skip_reason). skip_reason is None iff available is True."""
    if not OLLAMA_AVAILABLE:
        return False, "the 'ollama' package is not importable (see requirements.txt)"

    try:
        list_response = ollama.list()
    except Exception as e:
        return False, f"local Ollama server is not reachable ({e})"

    names = _extract_model_names(list_response)
    if any(n == LOCAL_MODEL or n.startswith(f"{LOCAL_MODEL}:") for n in names):
        return True, None
    return False, SETUP_INSTRUCTIONS


_AVAILABLE, _SKIP_REASON = _check_local_backend_available()

pytestmark = pytest.mark.skipif(not _AVAILABLE, reason=_SKIP_REASON or "local backend unavailable")


@pytest.fixture(autouse=True)
def _force_local_backend(monkeypatch):
    """_chat_completion reads the module-level pipeline.analyst.LLM_BACKEND directly
    (not config.models.LLM_BACKEND), so that's what must be patched for this test."""
    monkeypatch.setattr(analyst, "LLM_BACKEND", "local")


SAMPLE_SECTOR_CONTENT = (
    "### Fake BD Herald\n"
    "URL: https://example.com/fake-bd-herald\n\n"
    "Acme Construction Pte Ltd today announced a memorandum of understanding with "
    "BuildSmart Systems to jointly develop a digital twin platform for public housing "
    "estates, with the first pilot site targeted for completion by March 2027. Separately, "
    "BuildSmart Systems was shortlisted for a S$4.2 million smart facility management "
    "tender issued by a regional town council, with proposals due within six weeks."
)


def test_local_backend_free_text_call_returns_nonempty_string():
    """Mirrors _extract_sector's usage: json_schema=None, free-text extraction."""
    user_message = f"Sector: Partners\n\n{SAMPLE_SECTOR_CONTENT}"

    result = analyst._chat_completion(
        None,
        analyst.SECTOR_EXTRACT_PROMPT,
        user_message,
        800,
        json_schema=None,
    )

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_local_backend_schema_call_returns_valid_synthesis_json():
    """Mirrors _synthesize_sector's usage: SECTOR_SYNTHESIS_SCHEMA-constrained JSON output."""
    extraction_text = (
        "Fake BD Herald: Acme Construction Pte Ltd signed an MOU with BuildSmart Systems "
        "to jointly develop a digital twin platform for public housing estates, first pilot "
        "targeted for March 2027. BuildSmart Systems was shortlisted for a S$4.2 million "
        "smart facility management tender from a regional town council, proposals due in six weeks."
    )
    user_message = f"Sector: Partners\n\nExtracted signals:\n{extraction_text}"
    # Mirrors _synthesize_sector's local-only top-level-wrapper instruction exactly.
    user_message += '\n\nReturn a JSON object with a top-level "signals" array of the entries.'

    content = analyst._chat_completion(
        None,
        analyst.SECTOR_SYNTHESIS_PROMPT,
        user_message,
        800,
        json_schema=analyst.SECTOR_SYNTHESIS_SCHEMA,
    )

    result = json.loads(content)  # must not raise

    # Mirrors _synthesize_sector's own dict-unwrap tolerance.
    if isinstance(result, dict):
        result = result.get("signals", list(result.values())[0] if result else [])

    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, dict)
        assert "entity" in item
        assert "signal" in item
        assert "source_name" in item
