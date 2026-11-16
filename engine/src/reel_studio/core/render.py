"""Modo VSL: entrega scenes.json + tema + estilo ao Remotion."""

from __future__ import annotations

from pathlib import Path

from . import paths, proc
from .errors import ReelError

FPS = 30


def props(scenes: dict, theme: dict, style: dict) -> dict:
    return {"scenes": scenes["scenes"], "theme": theme, "style": style, "fps": FPS}


def args(npx: str, props_file: Path, out: Path) -> list[str]:
    return [npx, "remotion", "render", "src/index.ts", "Reel", str(out),
            f"--props={props_file}", "--codec=h264"]


def execute(scenes: dict, theme: dict, style: dict, workdir: Path, dry_run: bool) -> Path:
    if style["renderer"] != "remotion":
        raise ReelError(f"O estilo {style['id']} usa {style['renderer']}, previsto para a fase 3.")
    out = workdir / "output" / f"vsl-{style['id']}-{theme['id']}.mp4"
    props_file = paths.write_json(workdir / "render-props.json", props(scenes, theme, style))
    rdir = paths.render_dir()
    cmd = args("npx", props_file, out)
    if dry_run:
        print("dry-run:", " ".join(cmd), f"(em {rdir})")
        return out
    if not (rdir / "node_modules").is_dir():
        raise ReelError(f"Instale o render uma vez: cd {rdir} && npm install")
    npx = proc.require_bin("npx", "Instale o Node.js 18 ou mais novo.")
    out.parent.mkdir(exist_ok=True)
    proc.run([npx, *cmd[1:]], cwd=rdir)
    return out
