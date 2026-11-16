"""Modo corte: recorta, enquadra em 9:16 e queima a legenda do tema."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from . import frames, proc
from .captions import H, W, build_ass
from .errors import ReelError
from .frames import Analysis, Region

LAYOUTS = ("fill", "zoom", "fit")
BLUR = "boxblur=20:5"


@dataclass(frozen=True)
class Layout:
    kind: str = "fill"
    anchor: float = 0.5
    region: Region | None = None

    def describe(self, size: tuple[int, int]) -> str:
        return f"{self.kind} ({size[0]}x{size[1]})"


@dataclass(frozen=True)
class CutJob:
    clip_id: str
    ass_name: str
    ass_text: str
    out: Path
    args: list[str]
    layout: Layout = Layout()
    size: tuple[int, int] = (W, H)


ANCHORS = {"left": 0.0, "center": 0.5, "right": 1.0}


def parse_anchor(value: str | None) -> float | None:
    """Aceita left, center, right ou um número de 0 a 1 (SEG-01)."""
    if value is None:
        return None
    if value in ANCHORS:
        return ANCHORS[value]
    try:
        anchor = float(value)
    except ValueError:
        anchor = -1.0
    if not 0.0 <= anchor <= 1.0:
        raise ReelError("--anchor deve ser left, center, right ou um número de 0 a 1.")
    return anchor


def validate_layout(layout: str | None) -> str | None:
    if layout is not None and layout not in LAYOUTS:
        raise ReelError(f"--layout inválido: {layout!r}. Use {', '.join(LAYOUTS)}.")
    return layout


def choose_layout(size: tuple[int, int], analysis: Analysis | None) -> Layout:
    """Escolhe o layout sem parâmetro da pessoa (fill, zoom ou fit)."""
    width, height = size
    if width <= height:
        return Layout("fill")
    if analysis is None:
        return Layout("fit")
    if analysis.face_x is not None:
        sw = width * H / height
        anchor = (analysis.face_x * sw - W / 2) / (sw - W)
        return Layout("fill", anchor=min(max(anchor, 0.0), 1.0))
    if analysis.region is not None:
        return Layout("zoom", region=analysis.region)
    return Layout("fit")


def _background() -> str:
    return f"[0:v]split[a][b];[a]scale={W}:{H},{BLUR}[bg];"


def video_filter(layout: Layout, size: tuple[int, int], ass_name: str) -> str:
    if layout.kind == "fill":
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H}:(iw-{W})*{layout.anchor:.4f}:0,ass={ass_name}")
    if layout.kind == "zoom" and layout.region is not None:
        r = layout.region
        cw, ch = _even(r.w * size[0]), _even(r.h * size[1])
        cx, cy = _even(r.x * size[0]), _even(r.y * size[1])
        fg = f"[b]crop={cw}:{ch}:{cx}:{cy},scale={W}:-2[fg];"
    else:
        fg = f"[b]scale={W}:-2[fg];"
    return f"{_background()}{fg}[bg][fg]overlay=(W-w)/2:(H-h)/2,ass={ass_name}"


def _even(v: float) -> int:
    return max(2, int(v) // 2 * 2)


def ffmpeg_args(ffmpeg: str, video: Path, start: float, end: float,
                ass_name: str, out: Path, layout: Layout = Layout(),
                size: tuple[int, int] = (W, H)) -> list[str]:
    vf = video_filter(layout, size, ass_name)
    return [ffmpeg, "-y", "-loglevel", "error",
            "-ss", f"{start:.2f}", "-t", f"{end - start:.2f}", "-i", str(video),
            "-filter_complex" if layout.kind != "fill" else "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)]


def plan(video: Path, workdir: Path, clips: dict, transcript: dict, theme: dict,
         ffmpeg: str = "ffmpeg", size: tuple[int, int] | None = None,
         layout: str | None = None, anchor: float | None = None,
         analyzer: Callable[[Path, float, float], Analysis | None] = frames.analyze,
         ) -> list[CutJob]:
    validate_layout(layout)
    if anchor is not None and not 0.0 <= anchor <= 1.0:
        raise ReelError("anchor fora de 0 a 1.")
    size = size or proc.probe_size(video)
    jobs = []
    for c in clips["clips"]:
        ass_name = f"{c['id']}.ass"
        out = workdir / "output" / f"{c['id']}-{theme['id']}.mp4"
        chosen = _resolve(size, layout, anchor, analyzer, video, c["start"], c["end"])
        jobs.append(CutJob(
            clip_id=c["id"], ass_name=ass_name,
            ass_text=build_ass(transcript, c["start"], c["end"], theme, c.get("hook", "")),
            out=out, layout=chosen, size=size,
            args=ffmpeg_args(ffmpeg, video, c["start"], c["end"], ass_name, out, chosen, size),
        ))
    return jobs


def _resolve(size, layout, anchor, analyzer, video, start, end) -> Layout:
    if layout is None:
        chosen = choose_layout(size, analyzer(video, start, end) if size[0] > size[1] else None)
    elif layout == "zoom":
        # zoom manual precisa de região; sem análise cai no fit
        analysis = analyzer(video, start, end)
        chosen = Layout("zoom", region=analysis.region) if analysis and analysis.region \
            else Layout("fit")
    else:
        chosen = Layout(layout)
    if anchor is not None and chosen.kind == "fill":
        chosen = Layout("fill", anchor=anchor)
    return chosen


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
