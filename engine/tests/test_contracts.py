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


def test_estilo_isometrico_declara_ink_e_fundo_proprio():
    style = contracts.load_style("isometric-pastel")
    assert style["background"] == "own"
    assert style["look"]["ink"].startswith("#")


def test_look_ink_aceita_texto_e_rejeita_outro_tipo():
    style = contracts.load_style("isometric-pastel")
    contracts.validate("style", style)
    with pytest.raises(ContractError):
        contracts.validate("style", {**style, "look": {**style["look"], "ink": 7}})
