"""Varredura de dados sensíveis (segredos, tokens, e-mails): só rótulos, nunca o valor (SEG-05)."""

from __future__ import annotations

import re

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("chave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chave sk-", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("token Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")),
    ("bearer", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}", re.IGNORECASE)),
    ("segredo atribuído", re.compile(
        r"\b(?:api[_-]?key|secret|token|password|senha)\b\s*[:=]\s*['\"]?[^\s'\"]{8,}",
        re.IGNORECASE)),
    ("e-mail", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
)

MEDIA_WARNING = ("a gravação usada em `media` pode mostrar dados sensíveis na tela "
                 "(chaves, e-mails, painéis): confira o trecho antes de publicar.")


def scan(text: str) -> list[str]:
    """Rótulos dos tipos de dado sensível achados no texto, sem repetição e sem o valor."""
    return [label for label, rx in PATTERNS if rx.search(text or "")]


def scene_texts(scene: dict) -> list[str]:
    """Textos que a cena exibe ou fala."""
    parts = [scene.get("narration") or "", scene.get("text") or "",
             *(scene.get("steps") or []), *(scene.get("items") or [])]
    for side in (scene.get("left"), scene.get("right")):
        if side:
            parts += [side.get("label") or "", *(side.get("points") or [])]
    return parts


def warnings(scenes: list[dict], transcript: dict | None = None,
             share: str = "") -> list[str]:
    """Avisos (sem valores) para a transcrição, os textos das cenas e o `share`."""
    out: list[str] = []
    if transcript:
        text = " ".join(seg.get("text", "") for seg in transcript.get("segments", []))
        out += [f"transcrição contém {label}" for label in scan(text)]
    for i, scene in enumerate(scenes, 1):
        found = {label for part in scene_texts(scene) for label in scan(part)}
        out += [f"cena {i} contém {label}" for label in sorted(found)]
    out += [f"share contém {label}" for label in scan(share)]
    if any("media" in s for s in scenes):
        out.append(MEDIA_WARNING)
    return out
