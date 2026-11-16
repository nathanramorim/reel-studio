"""Modo corte: recorta, enquadra em 9:16 e queima a legenda do tema."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import proc
from .captions import H, W, build_ass


@dataclass(frozen=True)
class CutJob:
    clip_id: str
    ass_name: str
    ass_text: str
    out: Path
    args: list[str]


def ffmpeg_args(ffmpeg: str, video: Path, start: float, end: float,
                ass_name: str, out: Path) -> list[str]:
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},ass={ass_name}")
    return [ffmpeg, "-y", "-loglevel", "error",
            "-ss", f"{start:.2f}", "-t", f"{end - start:.2f}", "-i", str(video),
            "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)]


def plan(video: Path, workdir: Path, clips: dict, transcript: dict, theme: dict,
         ffmpeg: str = "ffmpeg") -> list[CutJob]:
    jobs = []
    for c in clips["clips"]:
        ass_name = f"{c['id']}.ass"
        out = workdir / "output" / f"{c['id']}-{theme['id']}.mp4"
        jobs.append(CutJob(
            clip_id=c["id"], ass_name=ass_name,
            ass_text=build_ass(transcript, c["start"], c["end"], theme, c.get("hook", "")),
            out=out, args=ffmpeg_args(ffmpeg, video, c["start"], c["end"], ass_name, out),
        ))
    return jobs


def execute(jobs: list[CutJob], workdir: Path) -> list[Path]:
    proc.require_bin("ffmpeg", proc.FFMPEG_HINT)
    (workdir / "output").mkdir(exist_ok=True)
    done = []
    for job in jobs:
        (workdir / job.ass_name).write_text(job.ass_text, encoding="utf-8")
        # cwd na pasta do vídeo: o filtro ass recebe nome relativo, sem escapar caminho
        proc.run(job.args, cwd=workdir)
        done.append(job.out)
    return done
