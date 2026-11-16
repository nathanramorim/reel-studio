"""Transcrição para o menor texto possível enviado ao LLM (única forma de envio)."""

from __future__ import annotations


def compact(transcript: dict, start: float = 0.0, end: float | None = None) -> str:
    lines = []
    for s in transcript["segments"]:
        if s["end"] < start or (end is not None and s["start"] > end):
            continue
        text = " ".join(s["text"].split())
        if text:
            lines.append(f"[{s['start']:.1f}] {text}")
    return "\n".join(lines)


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)
