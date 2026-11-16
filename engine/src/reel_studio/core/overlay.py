"""Camada de componentes sobre o corte: Remotion transparente composto por cima do mp4 intacto."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

from . import contracts, contrast, deliver, paths, proc, render
from .cut import CutJob, video_rect
from .errors import ReelError

COMPOSITION = "Overlay"
INTRO_COMPOSITION = "Intro"
INTRO_SECONDS = 1.5
STYLE_ID = "forge-motion"
OVERLAYS = ("auto", "none")


@dataclass(frozen=True)
class IntroPlan:
    """Abertura animada: vídeo mudo do Remotion concatenado antes do corte (o corte não muda)."""

    dur: float
    props_file: Path
    clip: Path
    source: Path
    out: Path
    render_args: list[str]
    concat_args: list[str]


@dataclass(frozen=True)
class LayerPlan:
    """Passos extras de um corte com `overlays`; o comando do corte (`CutJob.args`) não muda."""

    clip_id: str
    length: float
    count: int
    props_file: Path
    layer: Path
    out: Path
    render_args: list[str]
    compose_args: list[str]
    intro: IntroPlan | None = None


def validate_mode(mode: str) -> str:
    if mode not in OVERLAYS:
        raise ReelError(f"--overlays aceita {', '.join(OVERLAYS)}; recebi {mode!r}.")
    return mode


def _data_uri(path: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def with_assets(theme: dict) -> dict:
    """Logo e mascote (confinados à pasta do tema) viram data URI: o render não lê disco."""
    brand = theme.get("brand")
    if not brand:
        return theme
    out = {k: v for k, v in brand.items() if k not in contracts.BRAND_ASSETS}
    for key in contracts.BRAND_ASSETS:
        if brand.get(key):
            out[f"{key}Uri"] = _data_uri(brand[key])
    return {**theme, "brand": out}


def layer_props(job: CutJob, theme: dict) -> dict:
    style = contracts.load_style(STYLE_ID)
    adjusted = with_assets(contrast.resolve(theme, style)[0])
    return {"overlays": list(job.overlays), "theme": adjusted,
            "style": render.resolved_style(style, adjusted), "fps": render.FPS,
            "length": round(job.end - job.start, 3),
            "frame": video_rect(job.layout, job.size), "layout": job.layout.kind,
            "presenter": job.presenter, "speech": [list(s) for s in job.speech]}


def intro_dur(job: CutJob) -> float:
    return float((job.intro or {}).get("dur", INTRO_SECONDS))


def intro_props(job: CutJob, theme: dict) -> dict:
    style = contracts.load_style(STYLE_ID)
    adjusted = with_assets(contrast.resolve(theme, style)[0])
    return {"text": (job.intro or {}).get("text") or job.hook, "theme": adjusted,
            "style": render.resolved_style(style, adjusted), "fps": render.FPS,
            "length": intro_dur(job)}


def intro_render_args(npx: str, props_file: Path, clip: Path) -> list[str]:
    return [npx, "remotion", "render", "src/index.ts", INTRO_COMPOSITION, str(clip),
            f"--props={props_file}", "--codec=h264", "--pixel-format=yuv420p"]


def concat_args(ffmpeg: str, intro: Path, cut: Path, out: Path, dur: float) -> list[str]:
    """Abertura (áudio mudo) e corte em sequência; o corte só é recodificado."""
    fps = render.FPS
    graph = (f"[0:v]fps={fps},format=yuv420p,setsar=1[v0];"
             f"[2:v]fps={fps},format=yuv420p,setsar=1[v1];"
             "[1:a]aformat=sample_fmts=fltp:channel_layouts=stereo[a0];"
             "[2:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
             "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    return [ffmpeg, "-y", "-loglevel", "error", "-i", str(intro),
            "-f", "lavfi", "-t", f"{dur:.2f}", "-i", "anullsrc=r=48000:cl=stereo", "-i", str(cut),
            "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(out)]


def render_args(npx: str, props_file: Path, layer: Path) -> list[str]:
    return [npx, "remotion", "render", "src/index.ts", COMPOSITION, str(layer),
            f"--props={props_file}", "--codec=prores", "--prores-profile=4444",
            "--pixel-format=yuva444p10le", "--image-format=png"]


def compose_args(ffmpeg: str, cut: Path, layer: Path, out: Path) -> list[str]:
    """Sobrepõe a camada ao corte; o áudio do corte é copiado sem mexer."""
    return [ffmpeg, "-y", "-loglevel", "error", "-i", str(cut), "-i", str(layer),
            "-filter_complex", "[0:v][1:v]overlay=format=auto,format=yuv420p[v]",
            "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20", "-c:a", "copy", "-movflags", "+faststart", str(out)]


def needs_layer(job: CutJob) -> bool:
    return bool(job.overlays or job.presenter)


def plan(jobs: list[CutJob], workdir: Path, npx: str = "npx", ffmpeg: str = "ffmpeg",
         ) -> list[LayerPlan]:
    """Passos extras por corte (camada e abertura); não escreve nada (`--dry-run`)."""
    plans = []
    for j in jobs:
        if not (needs_layer(j) or j.intro is not None):
            continue
        layer = workdir / f"{j.clip_id}.layer.mov"
        props_file = workdir / f"{j.clip_id}.layer.json"
        out = j.out.with_name(f"{j.out.stem}-overlay{j.out.suffix}") if needs_layer(j) else j.out
        intro = None
        if j.intro is not None:
            clip = workdir / f"{j.clip_id}.intro.mp4"
            final = out.with_name(f"{out.stem}-abertura{out.suffix}")
            iprops = workdir / f"{j.clip_id}.intro.json"
            intro = IntroPlan(
                dur=intro_dur(j), props_file=iprops, clip=clip, source=out, out=final,
                render_args=intro_render_args(npx, iprops, clip),
                concat_args=concat_args(ffmpeg, clip, out, final, intro_dur(j)))
        plans.append(LayerPlan(
            clip_id=j.clip_id, length=round(j.end - j.start, 3), count=len(j.overlays),
            props_file=props_file, layer=layer, out=out,
            render_args=render_args(npx, props_file, layer) if needs_layer(j) else [],
            compose_args=compose_args(ffmpeg, j.out, layer, out) if needs_layer(j) else [],
            intro=intro))
    return plans


def execute(plans: list[LayerPlan], jobs: list[CutJob], theme: dict, workdir: Path) -> list[Path]:
    """Renderiza a camada e a abertura, compõe, e apaga os intermediários, mesmo em falha."""
    if not plans:
        return []
    rdir = paths.render_dir()
    if not (rdir / "node_modules").is_dir():
        raise ReelError(f"Instale o render uma vez: cd {rdir} && npm install")
    npx = proc.require_bin("npx", "Instale o Node.js 18 ou mais novo.")
    by_id = {j.clip_id: j for j in jobs}
    done = []
    for p in plans:
        try:
            if p.render_args:
                paths.write_json(p.props_file, layer_props(by_id[p.clip_id], theme))
                proc.run([npx, *p.render_args[1:]], cwd=rdir)
                proc.run(p.compose_args, cwd=workdir)
                deliver.apply_poster(p.compose_args[0], p.out, p.length,
                                     p.out.with_name(f"{p.out.stem}-poster.jpg"))
                done.append(p.out)
            if p.intro:
                paths.write_json(p.intro.props_file, intro_props(by_id[p.clip_id], theme))
                proc.run([npx, *p.intro.render_args[1:]], cwd=rdir)
                proc.run(p.intro.concat_args, cwd=workdir)
                done.append(p.intro.out)
        finally:
            for tmp in (p.layer, p.props_file):
                tmp.unlink(missing_ok=True)
            if p.intro:
                p.intro.clip.unlink(missing_ok=True)
                p.intro.props_file.unlink(missing_ok=True)
    return done
