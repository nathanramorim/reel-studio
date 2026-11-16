"""Borda do motor: argumentos, validação e saída curta (boa para agentes)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from .core import audio, contracts, cut, glossary, paths, render
from .core.compact import compact, estimate_tokens
from .core.errors import ReelError
from .core.llm import LLMClient
from .core.project import Project

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="reel-studio: reels verticais a partir de vídeos gravados.")

Video = Annotated[Path, typer.Argument(help="Arquivo de vídeo")]


def _load_env() -> None:
    for candidate in (Path.cwd() / ".env", paths.repo_root() / ".env"):
        if candidate.is_file():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                key, sep, value = line.partition("=")
                if sep and not line.lstrip().startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))
            return


Glossary = Annotated[Path | None, typer.Option(
    help="correcoes.json (padrão: o mais próximo do vídeo)")]


def _corrected(p: Project, file: Path | None = None,
               theme: dict | None = None) -> tuple[dict, str]:
    """Transcrição com o glossário aplicado em memória; o transcript.json segue cru."""
    t = p.require("transcript.json", f"reel-studio transcribe {p.video.name}")
    data = contracts.load("transcript", t)
    found = glossary.find(p.video, p.dir, theme or {}, file)
    if found is None:
        return data, ""
    data, n = glossary.apply(data, found.mapping)
    return data, f"glossário: {n} correções ({found.source})"


def _transcript(p: Project, file: Path | None = None) -> dict:
    return _corrected(p, file)[0]


@app.command()
def extract(video: Video,
            voice_only: Annotated[bool, typer.Option(help="Isola a voz (extra voice)")] = False):
    """Extrai o áudio (e opcionalmente só a voz)."""
    p = Project.open(video)
    wav = audio.extract(p.video, p.path("audio.wav"))
    typer.echo(f"audio: {wav}")
    if voice_only:
        typer.echo(f"voz: {audio.isolate_voice(wav, p.path('voice.wav'))}")


@app.command()
def transcribe(video: Video, model: str = "small", lang: str = "pt",
               force: Annotated[bool, typer.Option(help="Ignora o cache")] = False):
    """Transcreve local com Whisper (cache por vídeo)."""
    from .core.transcribe import transcribe as run

    p = Project.open(video)
    out = p.path("transcript.json")
    if out.is_file() and not force:
        typer.echo(f"transcript (cache): {out}")
        return
    wav = p.path("voice.wav") if p.path("voice.wav").is_file() else p.path("audio.wav")
    if not wav.is_file():
        wav = audio.extract(p.video, p.path("audio.wav"))
    data = contracts.validate("transcript", run(wav, model=model, language=lang or None))
    paths.write_json(out, data)
    typer.echo(f"transcript: {out} ({len(data['segments'])} segmentos, {data['duration']:.0f}s)")


@app.command(name="prompt-suggest")
def prompt_suggest_cmd(video: Video, max: int = 5, min_seconds: int = 15, max_seconds: int = 60,
                       glossary: Glossary = None):
    """Mostra o prompt do modo corte, para o agente gerar o JSON (sem rede, sem chave)."""
    from .core.suggest import prompt as build_prompt

    p = Project.open(video)
    system, user = build_prompt(_transcript(p, glossary), max_clips=max,
                                min_s=min_seconds, max_s=max_seconds)
    typer.echo(f"~{estimate_tokens(user)} tokens de transcrição\n")
    typer.echo("=== SYSTEM ===\n" + system)
    typer.echo("\n=== USER ===\n" + user)
    typer.echo(f"\nGere o JSON e grave com: reel-studio save-clips {video} --file SEU_JSON.json")


@app.command(name="save-clips")
def save_clips_cmd(video: Video, file: Path, max: int = 5,
                   min_seconds: int = 15, max_seconds: int = 60):
    """Valida o JSON de cortes (gerado pelo agente ou por você) e grava clips.json."""
    from .core.suggest import normalize

    p = Project.open(video)
    raw = paths.read_json(file)
    data = normalize(raw, _transcript(p), min_s=min_seconds, max_s=max_seconds, max_clips=max)
    paths.write_json(p.path("clips.json"), data)
    for c in data["clips"]:
        typer.echo(f"{c['id']}  {c['start']:.1f}s a {c['end']:.1f}s  {c['hook']}")
    typer.echo(f"revise e edite: {p.path('clips.json')}")


@app.command()
def suggest(video: Video, max: int = 5, min_seconds: int = 15, max_seconds: int = 60):
    """[Automação] Sugere cortes via OpenRouter (uma chamada) e grava clips.json.

    Dentro do Claude Code, prefira 'prompt-suggest' + 'save-clips': sem chave,
    sem chamada de rede nova, o próprio agente gera o JSON."""
    from .core.suggest import suggest as run

    _load_env()
    p = Project.open(video)
    t = _transcript(p)
    typer.echo(f"enviando ~{estimate_tokens(compact(t))} tokens de transcrição ao OpenRouter")
    data = run(t, LLMClient(), max_clips=max, min_s=min_seconds, max_s=max_seconds)
    paths.write_json(p.path("clips.json"), data)
    for c in data["clips"]:
        typer.echo(f"{c['id']}  {c['start']:.1f}s a {c['end']:.1f}s  {c['hook']}")
    typer.echo(f"revise e edite: {p.path('clips.json')}")


@app.command(name="prompt-script")
def prompt_script_cmd(video: Video, style: str, start: float = 0.0, end: float | None = None,
                      glossary: Glossary = None):
    """Mostra o prompt do modo VSL, para o agente gerar o JSON (sem rede, sem chave)."""
    from .core.script import prompt as build_prompt

    p = Project.open(video)
    system, user = build_prompt(_transcript(p, glossary), contracts.load_style(style),
                                start, end)
    typer.echo(f"~{estimate_tokens(user)} tokens de transcrição\n")
    typer.echo("=== SYSTEM ===\n" + system)
    typer.echo("\n=== USER ===\n" + user)
    cmd = f"reel-studio save-scenes {video} --style {style} --file SEU_JSON.json"
    typer.echo(f"\nGere o JSON e grave com: {cmd}")


@app.command(name="save-scenes")
def save_scenes_cmd(video: Video, style: str, file: Path, theme: str | None = None):
    """Valida o JSON de cenas (gerado pelo agente ou por você) e grava scenes.json."""
    from .core.script import normalize

    p = Project.open(video)
    raw = paths.read_json(file)
    data = normalize(raw, contracts.load_style(style), theme)
    paths.write_json(p.path("scenes.json"), data)
    total = sum(s["dur"] for s in data["scenes"])
    typer.echo(f"{len(data['scenes'])} cenas, {total:.0f}s. Revise: {p.path('scenes.json')}")


@app.command()
def script(video: Video, style: str, theme: str | None = None,
           start: float = 0.0, end: float | None = None):
    """[Automação] Gera o roteiro via OpenRouter e grava scenes.json.

    Dentro do Claude Code, prefira 'prompt-script' + 'save-scenes': sem chave,
    sem chamada de rede nova, o próprio agente gera o JSON."""
    from .core.script import script as run

    _load_env()
    p = Project.open(video)
    data = run(_transcript(p), contracts.load_style(style), LLMClient(), theme, start, end)
    paths.write_json(p.path("scenes.json"), data)
    total = sum(s["dur"] for s in data["scenes"])
    typer.echo(f"{len(data['scenes'])} cenas, {total:.0f}s. Revise: {p.path('scenes.json')}")


@app.command(name="cut")
def cut_cmd(video: Video, theme: str = "pessoal",
            layout: Annotated[str | None, typer.Option(
                help="Override raro: fill, zoom ou fit (padrão: automático)")] = None,
            anchor: Annotated[str | None, typer.Option(
                help="Override raro do fill: left, center, right ou 0 a 1")] = None,
            glossary: Glossary = None,
            dry_run: Annotated[bool, typer.Option(help="Só mostra o plano")] = False):
    """Recorta os clips aprovados, em 9:16, com legenda no tema."""
    p = Project.open(video)
    clips = contracts.load("clips", p.require("clips.json", f"reel-studio suggest {video}"))
    th = contracts.load_theme(theme)
    transcript, note = _corrected(p, glossary, th)
    if note:
        typer.echo(note)
    jobs = cut.plan(p.video, p.dir, clips, transcript, th,
                    layout=layout, anchor=cut.parse_anchor(anchor))
    for j in jobs:
        typer.echo(f"{j.clip_id} layout: {j.layout.describe(j.size)}")
    if dry_run:
        for j in jobs:
            typer.echo(f"dry-run {j.clip_id}: {j.out.name}")
        return
    for out in cut.execute(jobs, p.dir):
        typer.echo(f"reel: {out}")


@app.command(name="render")
def render_cmd(video: Video, theme: str = "pessoal", style: str | None = None,
               dry_run: Annotated[bool, typer.Option(help="Só mostra o comando")] = False):
    """Renderiza o scenes.json aprovado com Remotion."""
    p = Project.open(video)
    scenes = contracts.load("scenes", p.require("scenes.json", f"reel-studio script {video}"))
    st = contracts.load_style(style or scenes["style"])
    out = render.execute(scenes, contracts.load_theme(theme), st, p.dir, dry_run)
    typer.echo(f"vsl: {out}")


@app.command()
def status(video: Video):
    """Mostra o que já existe para o vídeo."""
    p = Project.open(video)
    for name, ok in p.status().items():
        typer.echo(f"{'ok ' if ok else '-- '} {name}")
    typer.echo(f"pasta: {p.dir}")


@app.command()
def validate():
    """Valida todos os temas e estilos contra os contratos."""
    for t in paths.list_themes():
        contracts.load_theme(t)
    for s in paths.list_styles():
        contracts.load_style(s)
    themes = ", ".join(paths.list_themes())
    styles = ", ".join(paths.list_styles())
    typer.echo(f"ok: temas {themes} | estilos {styles}")


@app.command(name="list")
def list_cmd():
    """Lista temas e estilos disponíveis."""
    typer.echo("temas:   " + ", ".join(paths.list_themes()))
    for s in paths.list_styles():
        st = contracts.load_style(s)
        typer.echo(f"estilo:  {s} ({st['renderer']}) para {st.get('best_for', '')}")


def main() -> None:
    try:
        app(standalone_mode=False)
    except ReelError as e:
        typer.secho(str(e), fg="red", err=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
