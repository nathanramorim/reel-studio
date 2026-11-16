import json
import sys
import types
from pathlib import Path

import pytest
from typer.testing import CliRunner

from reel_studio import cli
from reel_studio.cli import app
from reel_studio.core import transcribe as tr
from reel_studio.core.errors import ReelError


def test_av_fixado_no_extra_transcribe():
    text = (Path(__file__).parents[1] / "pyproject.toml").read_text()
    line = next(entry for entry in text.splitlines() if entry.startswith("transcribe ="))
    assert '"av<17"' in line


def test_modelo_invalido_e_rejeitado():
    with pytest.raises(ReelError):
        tr.resolve_model("gigante")


def test_modelo_padrao_e_variavel_de_ambiente(monkeypatch):
    monkeypatch.delenv("REEL_WHISPER_MODEL", raising=False)
    assert tr.resolve_model(None) == "small"
    monkeypatch.setenv("REEL_WHISPER_MODEL", "medium")
    assert tr.resolve_model(None) == "medium"
    assert tr.resolve_model("tiny") == "tiny"


def test_modelo_large_v3_chega_ao_whisper(monkeypatch):
    seen = {}

    class FakeModel:
        def __init__(self, name, **_):
            seen["model"] = name

        def transcribe(self, _audio, **kw):
            seen["prompt"] = kw["initial_prompt"]
            return [], types.SimpleNamespace(language="pt", duration=1.0)

    fake = types.SimpleNamespace(WhisperModel=FakeModel)
    monkeypatch.setitem(sys.modules, "faster_whisper", fake)
    data = tr.transcribe(Path("a.wav"), model="large-v3", initial_prompt="checagem")
    assert seen == {"model": "large-v3", "prompt": "checagem"}
    assert data["model"] == "large-v3" and data["initial_prompt"] == "checagem"


def test_prompt_une_glossario_e_tema_sem_repetir():
    out = tr.build_prompt({"checaja": "checagem", "checage": "checagem", "x": "Forge SDD"},
                          ["Forge SDD", "feature"], "extra")
    assert out.split(", ") == ["extra", "Forge SDD", "feature", "checagem"]


def test_prompt_respeita_o_limite():
    out = tr.build_prompt({f"e{i}": f"termo-numero-{i}" for i in range(500)}, [])
    assert 0 < len(out) <= tr.MAX_PROMPT_CHARS


class _Proj:
    def __init__(self, d):
        self.video, self.dir = d / "v.mp4", d

    def path(self, name):
        return self.dir / name


def _cli(monkeypatch, tmp_path, calls):
    (tmp_path / "audio.wav").write_bytes(b"x")
    monkeypatch.setattr(cli.Project, "open", lambda _v: _Proj(tmp_path))

    def fake(_wav, model, language, initial_prompt):
        calls.append((model, initial_prompt))
        return {"language": "pt", "duration": 1.0, "model": model,
                "initial_prompt": initial_prompt, "segments": []}
    monkeypatch.setattr(tr, "transcribe", fake)


def test_cache_muda_modelo_ou_prompt_invalida(monkeypatch, tmp_path):
    calls: list = []
    _cli(monkeypatch, tmp_path, calls)
    monkeypatch.delenv("REEL_WHISPER_MODEL", raising=False)
    run = CliRunner().invoke
    assert run(app, ["transcribe", "v.mp4"]).exit_code == 0
    assert run(app, ["transcribe", "v.mp4"]).exit_code == 0
    assert len(calls) == 1  # igual reaproveita
    assert run(app, ["transcribe", "v.mp4", "--model", "medium"]).exit_code == 0
    assert run(app, ["transcribe", "v.mp4", "--model", "medium", "--prompt", "x"]).exit_code == 0
    assert [c[0] for c in calls] == ["small", "medium", "medium"]
    assert json.loads((tmp_path / "transcript.json").read_text())["initial_prompt"] == "x"
