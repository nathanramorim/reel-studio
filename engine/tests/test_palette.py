from reel_studio.core import contracts, contrast, palette


def test_tokens_viram_hex_do_tema():
    forge = contracts.load_theme("forge")["colors"]
    assert palette.resolve(["accent", "accent2", "success"], forge) == [
        "#4f8ef7", "#8aa4ff", "#3ecf8e"]


def test_token_ausente_cai_em_tons_do_accent():
    colors = contracts.load_theme("busize")["colors"]
    colors.pop("warn", None)
    out = palette.resolve(["accent", "warn"], colors)
    assert out[0] == colors["accent"]
    assert out[1] == palette.derived(colors["accent"], 2)[1]
    assert out[1] != colors["accent"]


def test_tons_derivados_mais_claro_e_mais_escuro():
    base, lighter, darker = palette.derived("#4f8ef7", 3)
    assert contrast.luminance(lighter) > contrast.luminance(base) > contrast.luminance(darker)


def test_hex_literal_passa_direto():
    assert palette.resolve_color("#123456", {}, "#000000") == "#123456"
