"""Execução de processos externos: sempre lista de argumentos, nunca shell (SEG-03)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .errors import ReelError


def require_bin(name: str, hint: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ReelError(f"'{name}' não encontrado no PATH. {hint}")
    return path


def run(args: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise ReelError(f"Falhou: {Path(args[0]).name} (código {result.returncode})\n{tail}")


def capture(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise ReelError(f"Falhou: {Path(args[0]).name} (código {result.returncode})\n{tail}")
    return result.stdout


def probe_size(video: Path) -> tuple[int, int]:
    """Largura e altura do primeiro stream de vídeo, via ffprobe."""
    ffprobe = require_bin("ffprobe", FFMPEG_HINT)
    out = capture([ffprobe, "-v", "error", "-select_streams", "v:0",
                   "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)])
    try:
        w, h = (int(v) for v in out.strip().split(",")[:2])
    except ValueError:
        raise ReelError(f"Não consegui ler as dimensões de {video.name}.") from None
    return w, h


def probe_duration(video: Path) -> float:
    """Duração do contêiner em segundos, via ffprobe."""
    ffprobe = require_bin("ffprobe", FFMPEG_HINT)
    out = capture([ffprobe, "-v", "error", "-show_entries", "format=duration",
                   "-of", "csv=p=0", str(video)])
    try:
        return float(out.strip())
    except ValueError:
        raise ReelError(f"Não consegui ler a duração de {video.name}.") from None


FFMPEG_HINT = "Instale o ffmpeg (macOS: brew install ffmpeg; Windows: winget install ffmpeg)."
