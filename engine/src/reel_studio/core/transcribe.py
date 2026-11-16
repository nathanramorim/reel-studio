"""Transcrição local com faster-whisper (nada sai da máquina)."""

from __future__ import annotations

import os
from pathlib import Path

from .errors import ReelError

MODELS = ("tiny", "base", "small", "medium", "large-v3")
DEFAULT_MODEL = "small"
MAX_PROMPT_CHARS = 800   # ~200 tokens


def resolve_model(model: str | None) -> str:
    """Modelo pedido, ou REEL_WHISPER_MODEL, ou o padrão; só valores conhecidos (SEG-01)."""
    chosen = model or os.environ.get("REEL_WHISPER_MODEL") or DEFAULT_MODEL
    if chosen not in MODELS:
        raise ReelError(f"Modelo inválido: '{chosen}'. Use um de: {', '.join(MODELS)}.")
    return chosen


def build_prompt(glossary: dict[str, str], vocabulary: list[str], extra: str = "") -> str:
    """Dica de vocabulário: texto extra, termos do tema e valores do glossário, sem repetição."""
    seen: set[str] = set()
    terms: list[str] = []
    for term in [*vocabulary, *glossary.values()]:
        term = term.strip()
        if term and term.casefold() not in seen:
            seen.add(term.casefold())
            terms.append(term)
    prompt = extra.strip()
    for term in terms:
        candidate = f"{prompt}, {term}" if prompt else term
        if len(candidate) > MAX_PROMPT_CHARS:
            break
        prompt = candidate
    return prompt[:MAX_PROMPT_CHARS]


def transcribe(audio: Path, model: str = DEFAULT_MODEL, language: str | None = "pt",
               initial_prompt: str = "") -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        msg = "Transcrever precisa do extra 'transcribe': uv sync --extra transcribe"
        raise ReelError(msg) from e

    whisper = WhisperModel(model, device="auto", compute_type="auto")
    segments, info = whisper.transcribe(
        str(audio), language=language, word_timestamps=True, vad_filter=True,
        initial_prompt=initial_prompt or None,
    )
    out = []
    for s in segments:
        words = [
            {"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip()}
            for w in (s.words or [])
        ]
        out.append({"start": round(s.start, 2), "end": round(s.end, 2),
                    "text": s.text.strip(), "words": words})
    return {"language": info.language, "duration": round(info.duration, 2),
            "model": model, "initial_prompt": initial_prompt, "segments": out}
