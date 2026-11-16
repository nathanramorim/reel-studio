import json

import pytest
from typer.testing import CliRunner

from reel_studio import cli
from reel_studio.cli import app


class _Proj:
    def __init__(self, d):
        self.video, self.dir = d / "v.mp4", d

    def path(self, name):
        return self.dir / name


@pytest.fixture
def env(tmp_path, monkeypatch, transcript):
    monkeypatch.setattr(cli.Project, "open", lambda _v: _Proj(tmp_path))
    monkeypatch.setattr(cli, "_transcript", lambda *_: transcript)
    monkeypatch.setattr("reel_studio.core.suggest.normalize",
                        lambda raw, *_a, **_k: {"clips": []})
    monkeypatch.setattr("reel_studio.core.script.normalize",
                        lambda raw, *_a, **_k: {"scenes": []})
    monkeypatch.setattr(cli.contracts, "load_style", lambda s: {"id": s})
    f = tmp_path / "x.json"
    f.write_text(json.dumps({}))
    return str(f), tmp_path


def _run(*args):
    return CliRunner().invoke(app, list(args))


def test_flags_save_clips(env):
    f, d = env
    assert _run("save-clips", "v.mp4", "--file", f).exit_code == 0
    assert (d / "clips.json").is_file()
    (d / "clips.json").unlink()
    assert _run("save-clips", "v.mp4", f).exit_code == 0
    assert (d / "clips.json").is_file()


def test_flags_save_scenes(env):
    f, d = env
    assert _run("save-scenes", "v.mp4", "--style", "s", "--file", f).exit_code == 0
    assert (d / "scenes.json").is_file()
    (d / "scenes.json").unlink()
    assert _run("save-scenes", "v.mp4", "s", f).exit_code == 0
    assert (d / "scenes.json").is_file()


def test_flags_e_posicional_juntos_falham(env, capsys):
    f, _ = env
    with pytest.raises(cli.ReelError, match="só uma vez"):
        _run_raising("save-clips", "v.mp4", f, "--file", f)
    with pytest.raises(cli.ReelError, match="Falta"):
        _run_raising("save-clips", "v.mp4")
    with pytest.raises(cli.ReelError, match="Falta o estilo"):
        _run_raising("save-scenes", "v.mp4", "--file", f)


def _run_raising(*args):
    res = _run(*args)
    if res.exception:
        raise res.exception


# --- 05: entradas sem vídeo, voz e trilha ---
def test_conteudo_prompt_sem_video(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    post = tmp_path / "post.md"
    post.write_text("# Ideia\nAutomatize reels.", encoding="utf-8")
    r = CliRunner().invoke(app, ["prompt-script", "--content", str(post),
                                 "--style", "isometric-pastel", "--tone", "deadpan"])
    assert r.exit_code == 0, r.output
    assert "<conteudo>" in r.output and "--project ideia" not in r.output
    assert "save-scenes --project" in r.output
    assert (tmp_path / "reel-projects" / "post").is_dir()


def test_conteudo_com_segredo_avisa_sem_vazar(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    segredo = "AKI" + "AABCDEFGHIJKLMNOP"
    r = CliRunner().invoke(app, ["prompt-script", "--idea", f"use a chave {segredo}",
                                 "--style", "isometric-pastel"])
    avisos = [ln for ln in r.output.splitlines() if ln.startswith("aviso:")]
    assert avisos and all(segredo not in a for a in avisos)


def test_idea_e_conteudo_juntos_falham(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(app, ["prompt-script", "--idea", "x", "--content", "y.md",
                                 "--style", "isometric-pastel"])
    assert r.exit_code != 0


def test_voz_clone_sem_consentimento_ou_referencia_falha(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from reel_studio.core.project import Project
    p = Project.open_text("v")
    (p.dir / "scenes.json").write_text(json.dumps({"style": "forge-motion", "scenes": [
        {"type": "title", "dur": 3, "narration": "oi", "text": "x"}]}))
    base = ["render", "--project", "v", "--theme", "forge", "--voice", "clone", "--dry-run"]
    sem_flag = CliRunner().invoke(app, [*base, "--voice-ref", "ref.wav"])
    assert sem_flag.exit_code != 0 and "--confirm-own-voice" in str(sem_flag.exception)
    sem_ref = CliRunner().invoke(app, [*base, "--confirm-own-voice"])
    assert sem_ref.exit_code != 0 and "--voice-ref" in str(sem_ref.exception)


def test_dry_run_sem_video_nao_escreve_nada(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from reel_studio.core.project import Project
    p = Project.open_text("w")
    cena = {"type": "title", "dur": 3, "narration": "oi", "text": "x"}
    (p.dir / "scenes.json").write_text(json.dumps({
        "style": "forge-motion", "tone": "cinematic", "share": "Um reel.", "scenes": [cena]}))
    antes = sorted(q.name for q in p.dir.rglob("*"))
    r = CliRunner().invoke(app, ["render", "--project", "w", "--theme", "forge", "--dry-run"])
    assert r.exit_code == 0, r.output
    assert "trilha 100 BPM" in r.output and "share-copy.txt" in r.output
    assert sorted(q.name for q in p.dir.rglob("*")) == antes
