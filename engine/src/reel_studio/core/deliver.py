"""Entrega: pôster no quadro 0 e `share-copy.txt` (ARQ-05: nada é escrito em `--dry-run`)."""

from __future__ import annotations

import re
from pathlib import Path

from . import proc

POSTER_NAME = "poster.jpg"
SHARE_NAME = "share-copy.txt"
MAX_SENTENCES = 3
SETTLE = 0.9  # fração da primeira cena em que o texto já entrou por inteiro
SETTLE_MAX = 2.0


def poster_time(first_scene_seconds: float) -> float:
    """Instante do quadro parado mais forte: texto inteiro e assentado, antes de a cena sair."""
    return round(min(first_scene_seconds * SETTLE, SETTLE_MAX), 3)


def extract_args(ffmpeg: str, video: Path, at: float, poster: Path) -> list[str]:
    return [ffmpeg, "-y", "-loglevel", "error", "-ss", f"{at:.3f}", "-i", str(video),
            "-frames:v", "1", "-q:v", "2", str(poster)]


def replace_first_args(ffmpeg: str, video: Path, poster: Path, out: Path) -> list[str]:
    """Troca só o quadro 0 pelo pôster: duração, número de quadros e áudio não mudam."""
    return [ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-i", str(poster),
            "-filter_complex",
            "[1:v]scale=1080:1920,setsar=1,format=yuv420p[p];"
            "[0:v]format=yuv420p[v];[v][p]overlay=enable='eq(n,0)'[o]",
            "-map", "[o]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "18", "-fps_mode", "passthrough", "-c:a", "copy", "-movflags", "+faststart",
            str(out)]


def share_copy(share: str | None) -> str | None:
    """De 1 a 3 frases do `share`; sem `share`, não há arquivo."""
    text = (share or "").strip()
    if not text:
        return None
    sentences = re.findall(r"[^.!?]+[.!?]*", text)
    return " ".join(s.strip() for s in sentences[:MAX_SENTENCES] if s.strip()) + "\n"


def write_share(share: str | None, folder: Path) -> Path | None:
    body = share_copy(share)
    if body is None:
        return None
    out = folder / SHARE_NAME
    out.write_text(body, encoding="utf-8")
    return out


def apply_poster(ffmpeg: str, video: Path, first_scene_seconds: float, poster: Path) -> Path:
    """Tira o pôster do mp4 e o põe no quadro 0, regravando o mp4 no mesmo caminho."""
    proc.run(extract_args(ffmpeg, video, poster_time(first_scene_seconds), poster))
    tmp = video.with_name(f"{video.stem}.poster{video.suffix}")
    try:
        proc.run(replace_first_args(ffmpeg, video, poster, tmp))
        tmp.replace(video)
    finally:
        tmp.unlink(missing_ok=True)
    return poster
