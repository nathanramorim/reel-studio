"""Transcrição local com faster-whisper (nada sai da máquina)."""

from __future__ import annotations

from pathlib import Path

from .errors import ReelError


def transcribe(audio: Path, model: str = "small", language: str | None = "pt") -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        msg = "Transcrever precisa do extra 'transcribe': uv sync --extra transcribe"
        raise ReelError(msg) from e

    whisper = WhisperModel(model, device="auto", compute_type="auto")
    segments, info = whisper.transcribe(
        str(audio), language=language, word_timestamps=True, vad_filter=True
    )
    out = []
    for s in segments:
        words = [
            {"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip()}
            for w in (s.words or [])
        ]
        out.append({"start": round(s.start, 2), "end": round(s.end, 2),
                    "text": s.text.strip(), "words": words})
    return {"language": info.language, "duration": round(info.duration, 2), "segments": out}
