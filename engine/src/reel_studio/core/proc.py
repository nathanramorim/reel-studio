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


FFMPEG_HINT = "Instale o ffmpeg (macOS: brew install ffmpeg; Windows: winget install ffmpeg)."
