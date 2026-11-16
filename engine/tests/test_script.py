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


def _cena(a, b):
    return {"type": "title", "dur": 3, "narration": "x", "text": "t",
            "source": {"start": a, "end": b}}


def test_prompt_pede_source(transcript):
    from reel_studio.core.script import prompt

    system, _ = prompt(transcript, _style())
    assert "source" in system


def test_normalize_aceita_source_valido():
    data = normalize({"scenes": [_cena(0, 3), _cena(3, 6)]}, _style(), None, 100.0)
    assert data["scenes"][1]["source"] == {"start": 3, "end": 6}


@pytest.mark.parametrize("a,b", [(5, 2), (4, 4), (90, 120)])
def test_normalize_rejeita_source_invertido_ou_fora_do_video(a, b):
    with pytest.raises(ContractError, match="source"):
        normalize({"scenes": [_cena(a, b)]}, _style(), None, 100.0)


def test_normalize_rejeita_source_sobreposto():
    with pytest.raises(ContractError, match="sobreposto"):
        normalize({"scenes": [_cena(0, 5), _cena(4, 8)]}, _style(), None, 100.0)


# --- tempo de leitura (05-01) ---
def _leitura(scene):
    from reel_studio.core import script
    style = {"id": "isometric-pastel", "scene_types": ["title", "list", "cta"]}
    return script.normalize({"scenes": [scene]}, style, None)


def test_leitura_cena_curta_demais_e_rejeitada():
    from reel_studio.core.errors import ContractError
    texto = " ".join(["palavra"] * 10)  # 10 palavras: mínimo 3,4 s
    with pytest.raises(ContractError, match=r"Cena 1.*10 palavras.*3\.4s"):
        _leitura({"type": "title", "dur": 3, "narration": "", "text": texto})


def test_leitura_cena_adequada_passa():
    texto = " ".join(["palavra"] * 10)
    assert _leitura({"type": "title", "dur": 3.5, "narration": "", "text": texto})


def test_leitura_conta_itens_e_passos():
    from reel_studio.core.errors import ContractError
    with pytest.raises(ContractError, match="leitura|curto"):
        _leitura({"type": "list", "dur": 2, "narration": "",
                  "items": ["um dois três", "quatro cinco seis"]})


def test_leitura_texto_vazio_nao_exige_minimo():
    assert _leitura({"type": "cta", "dur": 1, "narration": "fale algo longo aqui"})
