import pytest

from reel_studio.core import contrast
from reel_studio.core.errors import ReelError


def test_razao_wcag_de_pares_conhecidos():
    assert contrast.ratio("#000000", "#ffffff") == pytest.approx(21)
    assert contrast.ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.01)


def test_gradiente_usa_o_pior_caso():
    stops = contrast.background_stops("linear-gradient(180deg,#141a3c,#ffffff)")
    assert stops == ["#141a3c", "#ffffff"]
    assert contrast.worst_ratio("#ffffff", stops) == pytest.approx(1.0)


def test_cor_invalida_e_rejeitada():
    with pytest.raises(ReelError):
        contrast.rgb("azul")
    with pytest.raises(ReelError):
        contrast.background_stops("transparent")


def test_shade_clareia_e_escurece():
    assert contrast.luminance(contrast.shade("#4f8ef7", 0.2)) > contrast.luminance("#4f8ef7")
    assert contrast.luminance(contrast.shade("#4f8ef7", -0.2)) < contrast.luminance("#4f8ef7")
