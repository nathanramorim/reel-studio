"""Única porta de rede do motor: chamada ao OpenRouter, sempre pedindo JSON."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable

import httpx

from .errors import ReelError

URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"

Sender = Callable[[dict], str]


def _http_sender(payload: dict) -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ReelError("Defina OPENROUTER_API_KEY no ambiente ou no arquivo .env.")
    try:
        r = httpx.post(URL, json=payload, timeout=120,
                       headers={"Authorization": f"Bearer {key}", "X-Title": "reel-studio"})
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        # Nunca inclui headers na mensagem (SEG-05)
        raise ReelError(f"OpenRouter respondeu {e.response.status_code}.") from None
    except httpx.HTTPError as e:
        raise ReelError(f"Falha de rede ao chamar o OpenRouter: {type(e).__name__}") from None
    return r.json()["choices"][0]["message"]["content"]


def parse_json(content: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ReelError(f"O modelo não devolveu JSON válido: {e}") from e
    if not isinstance(data, dict):
        raise ReelError("O modelo devolveu JSON, mas não um objeto.")
    return data


class LLMClient:
    def __init__(self, model: str | None = None, send: Sender | None = None):
        self.model = model or os.environ.get("REEL_STUDIO_MODEL", DEFAULT_MODEL)
        self._send = send or _http_sender

    def complete_json(self, system: str, user: str) -> dict:
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
        }
        return parse_json(self._send(payload))
