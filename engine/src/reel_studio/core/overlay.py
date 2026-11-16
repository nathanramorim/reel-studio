"""Camada de componentes sobre o corte: Remotion transparente composto por cima do mp4 intacto."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

from . import contracts, contrast, deliver, paths, proc, render
from .cut import CutJob
from .errors import ReelError

COMPOSITION = "Overlay"
STYLE_ID = "forge-motion"
OVERLAYS = ("auto", "none")


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
            "length": round(job.end - job.start, 3)}


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


def plan(jobs: list[CutJob], workdir: Path, npx: str = "npx", ffmpeg: str = "ffmpeg",
         ) -> list[LayerPlan]:
    """Um passo de camada por corte com `overlays`; não escreve nada (`--dry-run`)."""
    plans = []
    for j in jobs:
        if not j.overlays:
            continue
        layer = workdir / f"{j.clip_id}.layer.mov"
        props_file = workdir / f"{j.clip_id}.layer.json"
        out = j.out.with_name(f"{j.out.stem}-overlay{j.out.suffix}")
        plans.append(LayerPlan(
            clip_id=j.clip_id, length=round(j.end - j.start, 3), count=len(j.overlays),
            props_file=props_file, layer=layer, out=out,
            render_args=render_args(npx, props_file, layer),
            compose_args=compose_args(ffmpeg, j.out, layer, out)))
    return plans


def execute(plans: list[LayerPlan], jobs: list[CutJob], theme: dict, workdir: Path) -> list[Path]:
    """Renderiza a camada, compõe sobre o corte e apaga os intermediários, mesmo em falha."""
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
            paths.write_json(p.props_file, layer_props(by_id[p.clip_id], theme))
            proc.run([npx, *p.render_args[1:]], cwd=rdir)
            proc.run(p.compose_args, cwd=workdir)
            deliver.apply_poster(p.compose_args[0], p.out, p.length,
                                 p.out.with_name(f"{p.out.stem}-poster.jpg"))
        finally:
            p.layer.unlink(missing_ok=True)
            p.props_file.unlink(missing_ok=True)
        done.append(p.out)
    return done
