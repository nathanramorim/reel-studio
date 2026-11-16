import pytest

from reel_studio.core import contracts
from reel_studio.core.errors import ContractError
from reel_studio.core.script import normalize


def _style():
    return contracts.load_style("isometric-pastel")


def test_normalize_aceita_tipos_do_estilo():
    raw = {"scenes": [
        {"type": "title", "dur": 3, "narration": "x", "text": "Automatize"},
        {"type": "cta", "dur": 3, "narration": "y", "text": "Me segue"},
    ]}
    data = normalize(raw, _style(), theme_id="busize")
    assert data["theme"] == "busize"
    assert len(data["scenes"]) == 2


def test_normalize_rejeita_tipo_fora_do_estilo():
    raw = {"scenes": [{"type": "chart", "dur": 3, "narration": "x"}]}
    with pytest.raises(ContractError):
        normalize(raw, _style(), theme_id=None)


def test_prompt_nao_chama_rede(transcript):
    from reel_studio.core.script import prompt

    system, user = prompt(transcript, _style())
    assert "title" in system
    assert "[0.0]" in user
