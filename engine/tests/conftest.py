import json
from pathlib import Path

import pytest


@pytest.fixture
def transcript() -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / "transcript.json").read_text())


@pytest.fixture(autouse=True)
def _duracao_100(monkeypatch):
    """Vídeos de teste são falsos: a duração do ffprobe é fixada em 100 s."""
    from reel_studio.core import proc
    monkeypatch.setattr(proc, "probe_duration", lambda _v: 100.0)
