"""Extrair áudio e isolar a voz."""

from __future__ import annotations

import sys
from pathlib import Path

from . import proc


def extract_args(ffmpeg: str, video: Path, out: Path) -> list[str]:
    # 16 kHz mono: o formato que o Whisper usa, e pequeno no disco
    return [ffmpeg, "-y", "-loglevel", "error", "-i", str(video),
            "-vn", "-ac", "1", "-ar", "16000", str(out)]


def extract(video: Path, out: Path) -> Path:
    ffmpeg = proc.require_bin("ffmpeg", proc.FFMPEG_HINT)
    proc.run(extract_args(ffmpeg, video, out))
    return out


def isolate_args(audio: Path, workdir: Path) -> list[str]:
    return [sys.executable, "-m", "demucs", "--two-stems", "vocals", "-o", str(workdir), str(audio)]


def isolate_voice(audio: Path, out: Path) -> Path:
    try:
        import demucs  # noqa: F401
    except ImportError as e:
        raise proc.ReelError("Isolar voz precisa do extra 'voice': uv sync --extra voice") from e
    workdir = out.parent / "demucs"
    proc.run(isolate_args(audio, workdir))
    vocals = next(workdir.rglob("vocals.wav"), None)
    if not vocals:
        raise proc.ReelError("O demucs não gerou vocals.wav.")
    vocals.replace(out)
    return out
