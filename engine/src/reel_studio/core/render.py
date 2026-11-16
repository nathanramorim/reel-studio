"""Modo VSL: entrega scenes.json + tema + estilo ao Remotion; legenda (C) e áudio original (A)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from . import contrast, cut, deliver, frames, music, palette, paths, proc, sensitive, tone
from .captions import build_scene_ass, words_in
from .errors import ReelError
from .voice import Voice

FPS = 30
FADE = 0.05
CAPTIONS = ("narration", "none")
AUDIO = ("original", "none")


PUBLIC_DIR = "render-public"
FULL = {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}


@dataclass(frozen=True)
class Mix:
    captions: str = "narration"
    audio: str = "none"
    music: str = "auto"


def default_audio(scenes: list[dict]) -> str:
    """Padrão do `--audio`: a voz original quando todas as cenas têm `source`, senão nenhuma."""
    return "original" if scenes and all("source" in s for s in scenes) else "none"


def durations(scenes: list[dict], audio: str, voice: Voice | None = None,
              bpm: int | None = None) -> list[float]:
    """Duração efetiva da cena.

    Voz gerada: a do áudio gerado. Áudio original: o maior entre `dur` e o trecho (não corta a
    fala). Sem voz e com trilha (`bpm`): os limites se encaixam na batida mais próxima.
    """
    if voice:
        return list(voice.durations)
    out = []
    for s in scenes:
        src = s.get("source")
        out.append(max(s["dur"], src["end"] - src["start"]) if audio == "original" and src
                   else s["dur"])
    return music.snap_boundaries(out, bpm) if bpm else out


def music_bpm(scenes: dict, mix: Mix, voice: Voice | None, voice_planned: bool = False
              ) -> int | None:
    """BPM da trilha quando ela está ligada (padrão: sem voz); None quando desligada."""
    has_voice = mix.audio == "original" or voice is not None or voice_planned
    return tone.bpm(scenes.get("tone")) if music.is_on(mix.music, has_voice) else None


def reveal_words(narration: str, dur: float) -> list[dict]:
    """Sem tempos reais: as palavras da narração distribuídas por igual no tempo da cena."""
    words = narration.split()
    n = len(words)
    return [{"word": w, "start": round(dur * i / n, 3), "end": round(dur * (i + 1) / n, 3)}
            for i, w in enumerate(words)]


def scene_words(scene: dict, dur: float, audio: str, transcript: dict | None,
                generated: list[dict] | None = None) -> list[dict]:
    """Palavras com tempo, no tempo da cena: voz gerada, `source` da gravação ou uniforme."""
    raw = generated
    src = scene.get("source")
    if raw is None and audio == "original" and src and transcript:
        raw = words_in(transcript, src["start"], src["end"])
    if not raw:
        return reveal_words(scene.get("narration", ""), dur)
    return [{"word": w["word"], "start": round(min(max(w["start"], 0.0), dur), 3),
             "end": round(min(max(w["end"], 0.0), dur), 3)} for w in raw]


def media_item(scene: dict, video: Path, analyzer: Callable) -> dict | None:
    """Trecho real da gravação numa janela: arquivo no `--public-dir` e recorte automático."""
    media = scene.get("media")
    if not media:
        return None
    a, b = media["source"]["start"], media["source"]["end"]
    found = analyzer(video, a, b)
    r = found.region if found and found.region else None
    region = {"x": r.x, "y": r.y, "w": r.w, "h": r.h} if r else FULL
    return {"file": video.name, "start": a, "end": b, "region": region}


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


def props(scenes: dict, theme: dict, style: dict, audio: str = "none", *,
          transcript: dict | None = None, voice: Voice | None = None, bpm: int | None = None,
          video: Path | None = None, analyzer: Callable = frames.analyze) -> dict:
    adjusted, _ = contrast.resolve(theme, style)
    durs = durations(scenes["scenes"], audio, voice, bpm)
    items = []
    for i, (s, d) in enumerate(zip(scenes["scenes"], durs, strict=True)):
        item = {**s, "dur": d, "transition": tone.transition(scenes.get("tone"), s),
                "words": scene_words(s, d, audio, transcript,
                                     voice.words[i] if voice else None)}
        if "media" in s:
            if video is None:
                raise ReelError("`media` exige o vídeo de origem (a cena usa a gravação).")
            item["media"] = media_item(s, video, analyzer)
        items.append(item)
    return {"scenes": items, "theme": adjusted, "style": resolved_style(style, adjusted),
            "fps": FPS}


def args(npx: str, props_file: Path, out: Path, public_dir: Path | None = None) -> list[str]:
    cmd = [npx, "remotion", "render", "src/index.ts", "Reel", str(out),
           f"--props={props_file}", "--codec=h264"]
    return [*cmd, f"--public-dir={public_dir}"] if public_dir else cmd


def prepare_public(workdir: Path, video: Path) -> Path:
    """Pasta pública do Remotion: as fontes do render e a gravação (links, sem copiar, sem rede)."""
    target = workdir / PUBLIC_DIR
    target.mkdir(exist_ok=True)
    for src in [*paths.render_dir().joinpath("public").iterdir(), video]:
        link = target / src.name
        if not link.exists():
            link.symlink_to(src.resolve())
    return target


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


def mux_args(ffmpeg: str, silent: Path, source: Path | None, ass_name: str, out: Path,
             scenes: list[dict], durs: list[float], mix: Mix, music_wav: Path | None = None,
             voice_wav: Path | None = None) -> list[str]:
    """Junta vídeo, legenda e áudio: voz (original ou gerada) e trilha, esta abaixo da voz."""
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(silent)]
    filters: list[str] = []
    index, label = 1, None
    if mix.audio == "original" and source:
        cmd += ["-i", str(source)]
        filters.append(audio_filter(scenes, durs))
        index, label = index + 1, "[aout]"
    elif voice_wav:
        cmd += ["-i", str(voice_wav)]
        index, label = index + 1, f"[{index}:a]"
    if music_wav:
        cmd += ["-i", str(music_wav)]
        mixed, label = music.duck_filter(label is not None, index, label or "")
        filters.append(mixed)
    if filters:
        cmd += ["-filter_complex", ";".join(filters)]
    if label:
        cmd += ["-map", "0:v", "-map", label.strip("[]") if label.endswith(":a]") else label,
                "-c:a", "aac", "-b:a", "128k", "-shortest"]
    if mix.captions == "narration":
        cmd += ["-vf", f"ass={ass_name}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    else:
        cmd += ["-c:v", "copy"]
    return [*cmd, "-movflags", "+faststart", str(out)]


def execute(scenes: dict, theme: dict, style: dict, workdir: Path, dry_run: bool,
            source: Path | None, mix: Mix = Mix(), transcript: dict | None = None,
            voice: Voice | None = None, voice_planned: bool = False) -> Path:
    if style["renderer"] != "remotion":
        raise ReelError(f"O estilo {style['id']} usa {style['renderer']}, previsto para a fase 3.")
    check_mix(mix, scenes["scenes"])
    music.validate(mix.music)
    if mix.audio == "original" and source is None:
        raise ReelError("--audio original exige o vídeo de origem.")
    _, changed = contrast.resolve(theme, style)
    if changed:
        print(f"contraste: tema {theme['id']} sobre estilo {style['id']}: "
              f"cores ajustadas ({', '.join(changed)})")
    for warning in sensitive.warnings(scenes["scenes"], transcript, scenes.get("share", "")):
        print(f"aviso: {warning}")
    out = workdir / "output" / f"vsl-{style['id']}-{theme['id']}.mp4"
    bpm = music_bpm(scenes, mix, voice, voice_planned)
    has_media = any("media" in s for s in scenes["scenes"])
    silent = workdir / "render-silent.mp4"
    rdir = paths.render_dir()
    public = workdir / PUBLIC_DIR if has_media else None
    cmd = args("npx", workdir / "render-props.json", silent, public)
    durs = durations(scenes["scenes"], mix.audio, voice, bpm)
    if dry_run:
        print("dry-run:", " ".join(cmd), f"(em {rdir})")
        voice_note = " voz=clone" if voice_planned else ""
        print(f"dry-run: legenda={mix.captions} áudio={mix.audio}{voice_note} "
              f"duração={sum(durs):.2f}s ({len(durs)} cenas)")
        if bpm:
            plan = music.plan(durs, scenes.get("tone"))
            print(f"dry-run: trilha {plan['bpm']} BPM, {plan['length']:.2f}s, "
                  f"{len(plan['cuts'])} cortes na batida")
        print(f"dry-run: pôster no quadro 0 ({out.parent / deliver.POSTER_NAME})"
              + (f", {deliver.SHARE_NAME}" if scenes.get("share") else ""))
        return out
    if not (rdir / "node_modules").is_dir():
        raise ReelError(f"Instale o render uma vez: cd {rdir} && npm install")
    npx = proc.require_bin("npx", "Instale o Node.js 18 ou mais novo.")
    ffmpeg = proc.require_bin("ffmpeg", proc.FFMPEG_HINT)
    if mix.captions == "narration":
        cut.preflight(ffmpeg)
    out.parent.mkdir(exist_ok=True)
    if has_media:
        prepare_public(workdir, source)
    paths.write_json(workdir / "render-props.json",
                     props(scenes, theme, style, mix.audio, transcript=transcript, voice=voice,
                           bpm=bpm, video=source))
    proc.run([npx, *cmd[1:]], cwd=rdir)
    mixed = mix.captions == "narration" or mix.audio == "original" or voice or bpm
    music_wav = workdir / "music.wav" if bpm else None
    try:
        if mixed:
            ass_name = f"vsl-{style['id']}-{theme['id']}.ass"
            if mix.captions == "narration":
                (workdir / ass_name).write_text(
                    build_scene_ass(scenes["scenes"], durs, theme), encoding="utf-8")
            if music_wav:
                plan = music.plan(durs, scenes.get("tone"))
                music.write_wav(music_wav, plan["length"], plan["bpm"], plan["cuts"])
            proc.run(mux_args(ffmpeg, silent, source, ass_name, out, scenes["scenes"], durs, mix,
                              music_wav, voice.joined if voice else None), cwd=workdir)
        else:
            silent.replace(out)
        deliver.apply_poster(ffmpeg, out, durs[0], out.parent / deliver.POSTER_NAME)
        deliver.write_share(scenes.get("share"), out.parent)
    finally:
        silent.unlink(missing_ok=True)
        if music_wav:
            music_wav.unlink(missing_ok=True)
    return out
