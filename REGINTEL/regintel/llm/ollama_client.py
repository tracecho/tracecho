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


def _find_dotenv():
    start = Path(__file__).resolve()
    for parent in [start.parent, *start.parents[:6]]:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None


_env_path = _find_dotenv()
if _env_path is not None:
    load_dotenv(dotenv_path=str(_env_path), override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


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


def chat(messages, model=GEMINI_MODEL, format_json=False, temperature=0.0, timeout=120):
    """Call the configured Gemini model and return chat text or parsed JSON."""
    if not GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is missing. Add it to the workspace .env file.")
    if genai is None or types is None:
        raise GeminiError("google-genai is not installed. Install the Gemini SDK first.")

    client = genai.Client(api_key=GEMINI_API_KEY)
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
            model=model or GEMINI_MODEL,
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
