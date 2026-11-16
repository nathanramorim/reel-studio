import pytest

from reel_studio.core import contracts, paths
from reel_studio.core.errors import ContractError


def test_transcript_fixture_valida(transcript):
    contracts.validate("transcript", transcript)


def test_todos_os_temas_validam():
    for theme_id in paths.list_themes():
        contracts.load_theme(theme_id)


def test_todos_os_estilos_validam():
    for style_id in paths.list_styles():
        contracts.load_style(style_id)


def test_clips_invalido_rejeitado():
    with pytest.raises(ContractError):
        contracts.validate("clips", {"clips": [{"id": "x", "start": 0}]})


def test_pelo_menos_quatro_estilos():
    assert len(paths.list_styles()) >= 4


def test_temas_esperados_existem():
    assert {"pessoal", "busize", "forge", "exemplo"} <= set(paths.list_themes())


def test_estilo_isometrico_usa_fundo_do_tema():
    style = contracts.load_style("isometric-pastel")
    assert style["background"] == "theme"


def test_look_ink_aceita_texto_e_rejeita_outro_tipo():
    style = contracts.load_style("isometric-pastel")
    contracts.validate("style", {**style, "look": {**style["look"], "ink": "#1f2430"}})
    with pytest.raises(ContractError):
        contracts.validate("style", {**style, "look": {**style["look"], "ink": 7}})


def test_tema_aceita_glow_e_gradient_e_rejeita_gradient_curto():
    theme = contracts.load_theme("forge")
    assert theme["colors"]["glow"] == "#1e2a4a"
    bad = {**theme, "colors": {**theme["colors"], "gradient": ["#4f8ef7"]}}
    with pytest.raises(ContractError):
        contracts.validate("theme", bad)


def test_cena_aceita_source_e_rejeita_source_incompleto():
    cena = {"type": "title", "dur": 3, "narration": "x", "source": {"start": 1, "end": 4}}
    contracts.validate("scenes", {"style": "s", "scenes": [cena]})
    with pytest.raises(ContractError):
        contracts.validate("scenes", {"style": "s", "scenes": [{**cena, "source": {"start": 1}}]})
