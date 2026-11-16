"""Modo corte: escolhe os melhores trechos e alinha aos limites das frases."""

from __future__ import annotations

from . import contracts
from .compact import compact
from .llm import LLMClient

SYSTEM = (
    "Você escolhe trechos de um vídeo explicativo para virar reels verticais. "
    "Cada trecho precisa fazer sentido sozinho: começa no início de uma ideia e termina "
    "quando ela fecha. Prefira trechos com um gancho forte nos primeiros 3 segundos. "
    "Responda só JSON no formato "
    '{"clips":[{"start":0.0,"end":0.0,"hook":"frase de até 60 caracteres","reason":"curto"}]}.'
)


def build_user(text: str, max_clips: int, min_s: int, max_s: int) -> str:
    return (
        f"Escolha até {max_clips} trechos entre {min_s} e {max_s} segundos. "
        "Use os tempos entre colchetes. O hook fica no idioma da fala.\n\n" + text
    )


def _snap(transcript: dict, start: float, end: float) -> tuple[float, float]:
    segs = transcript["segments"]
    s = min(segs, key=lambda x: abs(x["start"] - start))["start"]
    e = min(segs, key=lambda x: abs(x["end"] - end))["end"]
    return s, max(e, s)


def normalize(raw: dict, transcript: dict, min_s: int, max_s: int, max_clips: int) -> dict:
    clips = []
    for c in raw.get("clips", []):
        try:
            start, end = _snap(transcript, float(c["start"]), float(c["end"]))
        except (KeyError, TypeError, ValueError):
            continue
        if end - start < min_s * 0.8:
            continue
        end = min(end, start + max_s)
        clips.append({"start": round(start, 2), "end": round(end, 2),
                      "hook": str(c.get("hook", "")).strip()[:60],
                      "reason": str(c.get("reason", "")).strip()})
    clips.sort(key=lambda c: c["start"])
    clips = clips[:max_clips]
    for i, c in enumerate(clips, 1):
        c["id"] = f"clip-{i:02d}"
    return contracts.validate("clips", {"clips": [dict(sorted(c.items())) for c in clips]})


def suggest(transcript: dict, llm: LLMClient, max_clips: int = 5,
            min_s: int = 15, max_s: int = 60) -> dict:
    raw = llm.complete_json(SYSTEM, build_user(compact(transcript), max_clips, min_s, max_s))
    return normalize(raw, transcript, min_s, max_s, max_clips)
