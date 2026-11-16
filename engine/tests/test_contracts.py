from pathlib import Path

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


# --- brand (05-02) ---
def _tema_com_brand(tmp_path, monkeypatch, brand, assets=("brand/logo.svg",)):
    import json
    for a in assets:
        f = tmp_path / "t" / a
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("<svg/>")
    tema = {"id": "t", "name": "T", "colors": {"bg": "#000000", "surface": "#111111",
            "text": "#ffffff", "muted": "#999999", "accent": "#4f8ef7"},
            "fonts": {"title": "Montserrat", "body": "Montserrat"},
            "caption": {"style": "line", "position": "bottom"}, "cta": {"text": "x"},
            "brand": brand}
    (tmp_path / "t.json").write_text(json.dumps(tema))
    monkeypatch.setattr(paths, "_theme_dirs", lambda: [tmp_path])


def test_brand_forge_resolve_ativos_dentro_da_pasta_do_tema():
    brand = contracts.load_theme("forge")["brand"]
    pasta = (paths.repo_root() / "themes" / "forge").resolve()
    for key in ("logo", "mascot"):
        assert Path(brand[key]).is_absolute() and Path(brand[key]).is_file()
        assert Path(brand[key]).is_relative_to(pasta)
    assert brand["panel"]["radius"] == 18 and brand["panel"]["dots"] == 3


def test_brand_tema_sem_brand_carrega_igual():
    assert "brand" not in contracts.load_theme("pessoal")


def test_brand_caminho_fora_da_pasta_do_tema_e_rejeitado(tmp_path, monkeypatch):
    _tema_com_brand(tmp_path, monkeypatch, {"logo": "../fora.svg"})
    with pytest.raises(ContractError, match="sai da pasta"):
        contracts.load_theme("t")


def test_brand_caminho_absoluto_ou_nao_svg_e_rejeitado(tmp_path, monkeypatch):
    for ruim in ("/etc/passwd.svg", "brand/logo.png"):
        _tema_com_brand(tmp_path, monkeypatch, {"logo": ruim})
        with pytest.raises(ContractError):
            contracts.load_theme("t")


def test_brand_ativo_inexistente_e_rejeitado(tmp_path, monkeypatch):
    _tema_com_brand(tmp_path, monkeypatch, {"logo": "brand/nao-existe.svg"})
    with pytest.raises(ContractError, match="não encontrado"):
        contracts.load_theme("t")


def test_brand_null_e_campos_opcionais(tmp_path, monkeypatch):
    _tema_com_brand(tmp_path, monkeypatch, {"logo": None, "mascot": None})
    assert contracts.load_theme("t")["brand"]["logo"] is None


# --- overlays, media e share (05-03) ---
def _clip(**extra):
    return {"clips": [{"id": "clip-01", "start": 10.0, "end": 20.0, "hook": "x", **extra}]}


def test_overlays_validos_passam():
    ov = [{"at": 0, "dur": 2, "type": "hook", "text": "Gancho"},
          {"at": 8, "dur": 2, "type": "logo"}]
    assert contracts.validate("clips", _clip(overlays=ov))


def test_overlays_pos_top_e_bottom_passam_e_outro_valor_e_rejeitado():
    ok = [{"at": 0, "dur": 2, "type": "keyword", "text": "x", "pos": "top"},
          {"at": 0, "dur": 2, "type": "step", "text": "y", "pos": "bottom"}]
    assert contracts.validate("clips", _clip(overlays=ok))
    with pytest.raises(ContractError):
        contracts.validate("clips", _clip(overlays=[{"at": 0, "dur": 1, "type": "step", "pos": "meio"}]))


def test_overlays_fora_do_corte_e_rejeitado():
    with pytest.raises(ContractError, match="fora do corte"):
        contracts.validate("clips", _clip(overlays=[{"at": 9, "dur": 2, "type": "cta"}]))


def test_overlays_tipo_invalido_e_texto_longo_sao_rejeitados():
    with pytest.raises(ContractError):
        contracts.validate("clips", _clip(overlays=[{"at": 0, "dur": 1, "type": "confete"}]))
    with pytest.raises(ContractError):
        contracts.validate("clips", _clip(overlays=[{"at": 0, "dur": 1, "type": "hook",
                                                      "text": "x" * 61}]))


def _cena(**extra):
    return {"style": "isometric-pastel",
            "scenes": [{"type": "title", "dur": 3, "narration": "n", **extra}]}


def test_media_e_share_validos_passam():
    data = {**_cena(media={"source": {"start": 1, "end": 4}}), "share": "x" * 280, "tone": "direto"}
    assert contracts.validate("scenes", data)


def test_media_invalida_e_share_longo_sao_rejeitados():
    with pytest.raises(ContractError):
        contracts.validate("scenes", _cena(media={"source": {"start": 1}}))
    with pytest.raises(ContractError):
        contracts.validate("scenes", {**_cena(), "share": "x" * 281})
