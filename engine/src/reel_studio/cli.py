"""Borda do motor: argumentos, validação e saída curta (boa para agentes)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, TypeVar

import typer

from .core import audio, contracts, cut, music, paths, proc, render
from .core import glossary as glossary_mod
from .core import overlay as overlay_mod
from .core import voice as voice_mod
from .core.compact import compact, estimate_tokens
from .core.errors import ReelError
from .core.llm import LLMClient
from .core.project import Project

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="reel-studio: reels verticais a partir de vídeos gravados.")

Video = Annotated[Path, typer.Argument(help="Arquivo de vídeo")]
OptVideo = Annotated[Path | None, typer.Argument(help="Arquivo de vídeo (ou use --project)")]
ProjectOpt = Annotated[str | None, typer.Option(
    "--project", help="Projeto sem vídeo (conteúdo ou ideia): reel-projects/<nome>")]


T = TypeVar("T")
FileArg = Annotated[Path | None, typer.Argument(help="JSON gerado (ou use --file)")]
FileOpt = Annotated[Path | None, typer.Option("--file", help="JSON gerado")]
StyleArg = Annotated[str | None, typer.Argument(help="Estilo (ou use --style)")]
StyleOpt = Annotated[str | None, typer.Option("--style", help="Estilo")]


def _either(positional: T | None, flag: T | None, what: str, option: str) -> T:
    """Aceita o valor posicional ou pela flag; os dois juntos, ou nenhum, é erro claro."""
    if positional is not None and flag is not None:
        raise ReelError(f"Informe {what} só uma vez: posicional ou {option}, não os dois.")
    value = positional if positional is not None else flag
    if value is None:
        raise ReelError(f"Falta {what}: use {option} ou passe como argumento posicional.")
    return value


def _load_env() -> None:
    for candidate in (Path.cwd() / ".env", paths.repo_root() / ".env"):
        if candidate.is_file():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                key, sep, value = line.partition("=")
                if sep and not line.lstrip().startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))
            return


def _open(video: Path | None, project: str | None) -> Project:
    """Projeto de um vídeo, ou de um texto sem vídeo (`--project`); um dos dois, nunca ambos."""
    if video is not None and project is not None:
        raise ReelError("Informe o vídeo ou --project, não os dois.")
    if video is None and project is None:
        raise ReelError("Falta o vídeo ou --project (entrada de conteúdo ou ideia).")
    return Project.open(video) if video is not None else Project.open_text(project)


Glossary = Annotated[Path | None, typer.Option(
    help="correcoes.json (padrão: o mais próximo do vídeo)")]


def _corrected(p: Project, file: Path | None = None,
               theme: dict | None = None) -> tuple[dict, str]:
    """Transcrição com o glossário aplicado em memória; o transcript.json segue cru."""
    t = p.require("transcript.json", f"reel-studio transcribe {p.video.name}")
    data = contracts.load("transcript", t)
    found = glossary_mod.find(p.video, p.dir, theme or {}, file)
    if found is None:
        return data, ""
    data, n = glossary_mod.apply(data, found.mapping)
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
def transcribe(video: Video,
               model: Annotated[str | None, typer.Option(
                   help="tiny|base|small|medium|large-v3 (padrão: REEL_WHISPER_MODEL ou small; "
                        "medium e large-v3 acertam mais o sotaque)")] = None,
               lang: str = "pt",
               theme: Annotated[str | None, typer.Option(
                   help="Tema cujo vocabulário alimenta o prompt")] = None,
               prompt: Annotated[str, typer.Option(help="Texto extra para o prompt")] = "",
               glossary: Glossary = None,
               force: Annotated[bool, typer.Option(help="Ignora o cache")] = False):
    """Transcreve local com Whisper (cache por vídeo, modelo e prompt)."""
    from .core import transcribe as tr

    chosen = tr.resolve_model(model)
    th = contracts.load_theme(theme) if theme else {}
    p = Project.open(video)
    found = glossary_mod.find(p.video, p.dir, th, glossary)
    hint = tr.build_prompt(found.mapping if found else {}, th.get("vocabulary", []), prompt)
    out = p.path("transcript.json")
    if out.is_file() and not force:
        cached = paths.read_json(out)
        if (cached.get("model", tr.DEFAULT_MODEL), cached.get("initial_prompt", "")) \
                == (chosen, hint):
            typer.echo(f"transcript (cache): {out}")
            return
        typer.echo("transcript em cache foi feito com outro modelo ou prompt: refazendo")
    wav = p.path("voice.wav") if p.path("voice.wav").is_file() else p.path("audio.wav")
    if not wav.is_file():
        wav = audio.extract(p.video, p.path("audio.wav"))
    data = contracts.validate(
        "transcript", tr.transcribe(wav, model=chosen, language=lang or None, initial_prompt=hint))
    paths.write_json(out, data)
    typer.echo(f"transcript: {out} ({len(data['segments'])} segmentos, {data['duration']:.0f}s,"
               f" modelo {chosen})")


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
def save_clips_cmd(video: Video, file_arg: FileArg = None, file_opt: FileOpt = None,
                   max: int = 5, min_seconds: int = 15, max_seconds: int = 60):
    """Valida o JSON de cortes (gerado pelo agente ou por você) e grava clips.json."""
    from .core.suggest import normalize

    file = _either(file_arg, file_opt, "o JSON de cortes", "--file")
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
def prompt_script_cmd(video: OptVideo = None, style_arg: StyleArg = None,
                      style_opt: StyleOpt = None, start: float = 0.0,
                      end: float | None = None, glossary: Glossary = None,
                      tone: Annotated[str | None, typer.Option(
                          help="default, polished, yc-parody, chaotic, deadpan, cinematic, "
                               "app-store")] = None,
                      content: Annotated[Path | None, typer.Option(
                          help="Texto ou markdown, no lugar do vídeo")] = None,
                      idea: Annotated[str | None, typer.Option(
                          help="Ideia livre, no lugar do vídeo")] = None,
                      project: ProjectOpt = None):
    """Mostra o prompt do roteiro (vídeo, conteúdo ou ideia), sem rede e sem chave."""
    from .core import script as script_mod

    style = _either(style_arg, style_opt, "o estilo", "--style")
    st = contracts.load_style(style)
    if content is not None or idea is not None:
        if content is not None and idea is not None:
            raise ReelError("Use --content ou --idea, não os dois.")
        if video is not None:
            raise ReelError("Conteúdo e ideia não usam vídeo: tire o argumento do vídeo.")
        text = content.read_text(encoding="utf-8") if content is not None else idea
        name = project or script_mod.slug(content.stem if content is not None else idea)
        p = Project.open_text(name)
        system, user, notes = script_mod.prompt_text(
            text, st, tone, "content" if content is not None else "idea")
        for note in notes:
            typer.echo(f"aviso: {note}; revise antes de gerar")
        where = f"--project {name}"
    else:
        p = _open(video, project)
        if p.video is None:
            raise ReelError("Sem vídeo: use --content ou --idea.")
        system, user = script_mod.prompt(_transcript(p, glossary), st, start, end, tone)
        where = str(video)
    typer.echo(f"~{estimate_tokens(user)} tokens de entrada\n")
    typer.echo("=== SYSTEM ===\n" + system)
    typer.echo("\n=== USER ===\n" + user)
    typer.echo(f"\nGere o JSON e grave com: reel-studio save-scenes {where} "
               f"--style {style} --file SEU_JSON.json")


@app.command(name="save-scenes")
def save_scenes_cmd(video: OptVideo = None, style_arg: StyleArg = None,
                    file_arg: FileArg = None, style_opt: StyleOpt = None,
                    file_opt: FileOpt = None, theme: str | None = None,
                    project: ProjectOpt = None):
    """Valida o JSON de cenas (gerado pelo agente ou por você) e grava scenes.json."""
    from .core.script import normalize

    style = _either(style_arg, style_opt, "o estilo", "--style")
    file = _either(file_arg, file_opt, "o JSON de cenas", "--file")
    p = _open(video, project)
    raw = paths.read_json(file)
    data = normalize(raw, contracts.load_style(style), theme,
                     proc.probe_duration(p.video) if p.video else None)
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
            overlays: Annotated[str, typer.Option(
                help="auto: componentes de `overlays` (clips.json) sobre o corte; none: ignora")
            ] = "auto",
            dry_run: Annotated[bool, typer.Option(help="Só mostra o plano")] = False):
    """Recorta os clips aprovados, em 9:16, com legenda no tema."""
    overlay_mod.validate_mode(overlays)
    p = Project.open(video)
    clips = contracts.load("clips", p.require("clips.json", f"reel-studio suggest {video}"))
    th = contracts.load_theme(theme)
    transcript, note = _corrected(p, glossary, th)
    if note:
        typer.echo(note)
    jobs = cut.plan(p.video, p.dir, clips, transcript, th, layout=layout,
                    anchor=cut.parse_anchor(anchor), overlays=overlays == "auto")
    layers = overlay_mod.plan(jobs, p.dir)
    for j in jobs:
        typer.echo(f"{j.clip_id} {j.start:.2f}-{j.end:.2f}s layout: {j.layout.describe(j.size)}")
    if dry_run:
        for j in jobs:
            typer.echo(f"dry-run {j.clip_id}: {j.out.name}")
        for layer in layers:
            typer.echo(f"dry-run {layer.clip_id}: camada de {layer.count} "
                       f"componentes, {layer.length:.2f}s -> {layer.out.name} (pôster no quadro 0)")
        return
    for out in cut.execute(jobs, p.dir):
        typer.echo(f"reel: {out}")
    for out in overlay_mod.execute(layers, jobs, th, p.dir):
        typer.echo(f"reel com componentes: {out}")


@app.command(name="render")
def render_cmd(video: OptVideo = None, theme: str = "pessoal", style: str | None = None,
               captions: Annotated[str, typer.Option(
                   help="narration: legenda queimada da narração; none")] = "narration",
               audio: Annotated[str | None, typer.Option(
                   help="original: áudio dos trechos `source`; none. "
                        "Padrão: original se todas as cenas têm `source`")] = None,
               music_mode: Annotated[str, typer.Option(
                   "--music", help="auto: liga sem voz; on; off. A trilha fica abaixo da voz")
               ] = "auto",
               voice: Annotated[str | None, typer.Option(
                   help="clone: voz gerada a partir de uma amostra (extra tts)")] = None,
               voice_ref: Annotated[str | None, typer.Option(
                   help="Amostra de voz (arquivo) ou `auto` para extrair da gravação")] = None,
               confirm_own_voice: Annotated[bool, typer.Option(
                   "--confirm-own-voice",
                   help="Confirmo que a voz é minha ou que tenho autorização")] = False,
               lang: Annotated[str, typer.Option(help="Idioma da voz gerada")] = "pt",
               project: ProjectOpt = None,
               dry_run: Annotated[bool, typer.Option(help="Só mostra o plano")] = False):
    """Renderiza o scenes.json aprovado com Remotion, com legenda, áudio e trilha por opção."""
    music.validate(music_mode)
    p = _open(video, project)
    scenes = contracts.load("scenes", p.require("scenes.json", "reel-studio save-scenes"))
    st = contracts.load_style(style or scenes["style"])
    transcript = _transcript(p) if p.path("transcript.json").is_file() and p.video else None
    generated = None
    if voice is not None:
        if voice != "clone":
            raise ReelError(f"--voice aceita clone; recebi {voice!r}.")
        generated = _clone(p, scenes, voice_ref, confirm_own_voice, lang, transcript, dry_run)
    if voice is not None or p.video is None:
        mode = "none"  # a voz gerada, ou nenhuma, no lugar do áudio da gravação
    else:
        mode = audio or render.default_audio(scenes["scenes"])
    out = render.execute(scenes, contracts.load_theme(theme), st, p.dir, dry_run, p.video,
                         render.Mix(captions, mode, music_mode), transcript, generated,
                         voice_planned=voice is not None)
    typer.echo(f"vsl: {out}")


def _clone(p: Project, scenes: dict, ref_arg: str | None, confirmed: bool, lang: str,
           transcript: dict | None, dry_run: bool) -> voice_mod.Voice | None:
    """Voz gerada: consentimento antes de tudo; no `--dry-run` nada é gerado nem escrito."""
    voice_mod.check_consent(confirmed, ref_arg is not None)
    if dry_run:
        return None
    if ref_arg == "auto":
        ref = _auto_ref(p, transcript)
    else:
        ref = voice_mod.require_consent(confirmed, Path(ref_arg).expanduser())
    from .core import transcribe as tr

    def align(wav: Path) -> dict:
        return tr.transcribe(wav, tr.resolve_model(None), language=lang)

    return voice_mod.synthesize(scenes["scenes"], ref, lang, p.dir,
                                voice_mod.chatterbox_synth(lang), align)


def _auto_ref(p: Project, transcript: dict | None) -> Path:
    if p.video is None or transcript is None:
        raise ReelError("--voice-ref auto exige um vídeo transcrito: rode transcribe antes.")
    wav = p.require("audio.wav", f"reel-studio extract {p.video.name}")
    return voice_mod.reference(transcript, wav, p.dir)


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
