"""Gemini chat client for the regulatory reasoning agent.

Uses the workspace .env values for GEMINI_API_KEY and GEMINI_MODEL while
keeping the existing chat(...) interface used by the LangGraph nodes.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover - raised clearly to caller when used
    genai = None
    types = None


def _load_workspace_dotenv():
    """Load .env files from the project and workspace hierarchy.

    Ensures the root workspace .env is loaded regardless of current working directory,
    while also supporting package-level or repo-level .env files.
    """
    candidates = []

    # 1. CWD and parents
    try:
        cwd = Path.cwd().resolve()
        candidates.extend([cwd / ".env", *[p / ".env" for p in cwd.parents[:4]]])
    except Exception:
        pass

    # 2. File ancestry:
    # start: .../regintel/llm/ollama_client.py
    # parents[0]: .../regintel/llm
    # parents[1]: .../regintel (package root)
    # parents[2]: .../REGINTEL (project root)
    # parents[3]: .../tracecho (workspace root)
    start = Path(__file__).resolve()
    for parent in [start.parent, *start.parents[:6]]:
        candidates.append(parent / ".env")

    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            if resolved not in seen and resolved.is_file():
                seen.add(resolved)
                load_dotenv(dotenv_path=str(resolved), override=False)
        except Exception:
            continue


# Initial environment load
_load_workspace_dotenv()


def get_gemini_api_key() -> str:
    """Retrieve GEMINI_API_KEY dynamically, reloading workspace .env if missing."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        _load_workspace_dotenv()
        key = os.getenv("GEMINI_API_KEY", "").strip()
    return key


def get_gemini_model() -> str:
    """Retrieve GEMINI_MODEL dynamically."""
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"


def check_gemini_config() -> dict:
    """Safe diagnostic reporting Gemini configuration without exposing secrets."""
    key = get_gemini_api_key()
    return {
        "key_present": bool(key),
        "key_length": len(key) if key else 0,
        "key_prefix": (key[:4] + "...") if len(key) >= 4 else "",
        "model": get_gemini_model(),
        "sdk_available": genai is not None and types is not None,
    }


# Backwards-compatible module-level bindings
GEMINI_API_KEY = get_gemini_api_key()
GEMINI_MODEL = get_gemini_model()


class GeminiError(RuntimeError):
    """Raised when the Gemini request fails or returns unusable content."""


OllamaError = GeminiError


def _messages_to_text(messages):
    parts = []
    for item in messages or []:
        role = str(item.get("role", "user")).upper()
        content = str(item.get("content", ""))
        if role in {"SYSTEM", "USER", "ASSISTANT"}:
            parts.append(f"{role}: {content}")
        else:
            parts.append(content)
    return "\n\n".join(parts)


def chat(messages, model=None, format_json=False, temperature=0.0, timeout=120):
    """Call the configured Gemini model and return chat text or parsed JSON."""
    api_key = get_gemini_api_key()
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is missing. Add it to the workspace .env file.")
    if genai is None or types is None:
        raise GeminiError("google-genai is not installed. Install the Gemini SDK first.")

    target_model = model or get_gemini_model()
    client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(api_version="v1beta")
    )
    prompt = _messages_to_text(messages)

    config = None
    if format_json:
        config = types.GenerateContentConfig(
            temperature=float(temperature),
            response_mime_type="application/json",
        )
    else:
        config = types.GenerateContentConfig(temperature=float(temperature))

    try:
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
            config=config,
        )
    except Exception as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    content = getattr(response, "text", "") or ""
    if not content:
        raise GeminiError("Gemini returned empty content.")

    if format_json:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    return content
