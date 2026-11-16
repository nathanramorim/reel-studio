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
