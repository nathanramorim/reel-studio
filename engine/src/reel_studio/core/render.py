"""Modo VSL: entrega scenes.json + tema + estilo ao Remotion; legenda (C) e áudio original (A)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import contrast, cut, palette, paths, proc
from .captions import build_scene_ass
from .errors import ReelError

FPS = 30
FADE = 0.05
CAPTIONS = ("narration", "none")
AUDIO = ("original", "none")


@dataclass(frozen=True)
class Mix:
    captions: str = "narration"
    audio: str = "none"


def durations(scenes: list[dict], audio: str) -> list[float]:
    """Duração efetiva: com áudio original, o maior entre `dur` e o trecho (não corta a fala)."""
    out = []
    for s in scenes:
        src = s.get("source")
        out.append(max(s["dur"], src["end"] - src["start"]) if audio == "original" and src
                   else s["dur"])
    return out


def check_mix(mix: Mix, scenes: list[dict]) -> None:
    if mix.captions not in CAPTIONS:
        raise ReelError(f"--captions aceita {', '.join(CAPTIONS)}; recebi {mix.captions!r}.")
    if mix.audio not in AUDIO:
        raise ReelError(f"--audio aceita {', '.join(AUDIO)}; recebi {mix.audio!r}.")
    if mix.audio == "original":
        missing = [str(i + 1) for i, s in enumerate(scenes) if "source" not in s]
        if missing:
            raise ReelError("--audio original exige `source` em todas as cenas. "
                            f"Sem source: cenas {', '.join(missing)}.")


def resolved_style(style: dict, theme: dict) -> dict:
    """Estilo com a paleta em hex do tema e a cor do texto sobre as placas."""
    colors = theme["colors"]
    look = dict(style.get("look", {}))
    fills = palette.resolve(look.get("palette", []) or ["accent"], colors)
    look["palette"] = fills
    if "stroke" in look:
        look["stroke"] = palette.resolve_color(look["stroke"], colors, colors["text"])
    look["ink"] = contrast.ink_for(fills, theme, style)
    return {**style, "look": look}


def props(scenes: dict, theme: dict, style: dict, audio: str = "none") -> dict:
    adjusted, _ = contrast.resolve(theme, style)
    items = [{**s, "dur": d} for s, d in zip(scenes["scenes"], durations(scenes["scenes"], audio),
                                             strict=True)]
    return {"scenes": items, "theme": adjusted, "style": resolved_style(style, adjusted),
            "fps": FPS}


def args(npx: str, props_file: Path, out: Path) -> list[str]:
    return [npx, "remotion", "render", "src/index.ts", "Reel", str(out),
            f"--props={props_file}", "--codec=h264"]


def audio_filter(scenes: list[dict], durs: list[float]) -> str:
    """Recorta o áudio de cada trecho de origem e emenda com fade curto, na duração da cena."""
    parts = []
    for i, (s, d) in enumerate(zip(scenes, durs, strict=True)):
        a, b = s["source"]["start"], s["source"]["end"]
        length = b - a
        fade = min(FADE, length / 2)
        parts.append(f"[1:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={fade},afade=t=out:st={length - fade:.3f}:d={fade},"
                     f"apad=whole_dur={d:.3f}[a{i}]")
    joined = "".join(f"[a{i}]" for i in range(len(scenes)))
    return ";".join(parts) + f";{joined}concat=n={len(scenes)}:v=0:a=1[aout]"


def mux_args(ffmpeg: str, silent: Path, source: Path, ass_name: str, out: Path,
             scenes: list[dict], durs: list[float], mix: Mix) -> list[str]:
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(silent)]
    if mix.audio == "original":
        cmd += ["-i", str(source), "-filter_complex", audio_filter(scenes, durs), "-map", "0:v",
                "-map", "[aout]", "-c:a", "aac", "-b:a", "128k", "-shortest"]
    if mix.captions == "narration":
        cmd += ["-vf", f"ass={ass_name}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    else:
        cmd += ["-c:v", "copy"]
    return [*cmd, "-movflags", "+faststart", str(out)]


def execute(scenes: dict, theme: dict, style: dict, workdir: Path, dry_run: bool,
            source: Path, mix: Mix = Mix()) -> Path:
    if style["renderer"] != "remotion":
        raise ReelError(f"O estilo {style['id']} usa {style['renderer']}, previsto para a fase 3.")
    check_mix(mix, scenes["scenes"])
    _, changed = contrast.resolve(theme, style)
    if changed:
        print(f"contraste: tema {theme['id']} sobre estilo {style['id']}: "
              f"cores ajustadas ({', '.join(changed)})")
    out = workdir / "output" / f"vsl-{style['id']}-{theme['id']}.mp4"
    mixed = mix.captions == "narration" or mix.audio == "original"
    silent = workdir / "render-silent.mp4" if mixed else out
    rdir = paths.render_dir()
    cmd = args("npx", workdir / "render-props.json", silent)
    durs = durations(scenes["scenes"], mix.audio)
    if dry_run:
        print("dry-run:", " ".join(cmd), f"(em {rdir})")
        print(f"dry-run: legenda={mix.captions} áudio={mix.audio} "
              f"duração={sum(durs):.2f}s ({len(durs)} cenas)")
        return out
    if not (rdir / "node_modules").is_dir():
        raise ReelError(f"Instale o render uma vez: cd {rdir} && npm install")
    npx = proc.require_bin("npx", "Instale o Node.js 18 ou mais novo.")
    ffmpeg = proc.require_bin("ffmpeg", proc.FFMPEG_HINT) if mixed else ""
    if mix.captions == "narration":
        cut.preflight(ffmpeg)
    paths.write_json(workdir / "render-props.json", props(scenes, theme, style, mix.audio))
    out.parent.mkdir(exist_ok=True)
    proc.run([npx, *cmd[1:]], cwd=rdir)
    if mixed:
        ass_name = f"vsl-{style['id']}-{theme['id']}.ass"
        if mix.captions == "narration":
            (workdir / ass_name).write_text(
                build_scene_ass(scenes["scenes"], durs, theme), encoding="utf-8")
        proc.run(mux_args(ffmpeg, silent, source, ass_name, out,
                          scenes["scenes"], durs, mix), cwd=workdir)
        silent.unlink(missing_ok=True)
    return out
