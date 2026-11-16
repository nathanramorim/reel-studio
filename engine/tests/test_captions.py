from reel_studio.core import contracts
from reel_studio.core.captions import ass_color, build_ass, ts


def test_ts_formata_centesimos():
    assert ts(0) == "0:00:00.00"
    assert ts(65.5) == "0:01:05.50"


def test_ass_color_formato_bgr():
    assert ass_color("#4f8ef7") == "&H00F78E4F"


def test_build_ass_contem_evento_e_hook(transcript):
    theme = contracts.load_theme("busize")
    out = build_ass(transcript, 0.0, 7.0, theme, hook="Automatize em 3 passos")
    assert "[Events]" in out
    assert "Automatize em 3 passos" in out
    assert "Dialogue:" in out
