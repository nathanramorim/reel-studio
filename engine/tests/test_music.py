import wave

import pytest

from reel_studio.core import music
from reel_studio.core.errors import ReelError


def _duracao(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def test_wav_tem_a_duracao_do_video(tmp_path):
    out = music.write_wav(tmp_path / "m.wav", 3.0, 120, [1.5])
    assert _duracao(out) == pytest.approx(3.0, abs=1 / music.RATE)


def test_saida_deterministica(tmp_path):
    a = music.write_wav(tmp_path / "a.wav", 2.0, 110, [1.0]).read_bytes()
    b = music.write_wav(tmp_path / "b.wav", 2.0, 110, [1.0]).read_bytes()
    assert a == b


def test_batida_encaixa_limite_proximo():
    # 120 BPM: batida a cada 0,5 s; 3,1 s -> 3,0 s (diferença 0,1 s)
    novas = music.snap_boundaries([3.1, 3.0], 120)
    assert novas[0] == pytest.approx(3.0)
    assert sum(novas) == pytest.approx(6.0, abs=0.01)


def test_batida_nao_encaixa_acima_da_tolerancia():
    # 60 BPM: batida a cada 1 s; 3,4 s fica a 0,4 s da batida: não passa de 0,25 s
    assert music.snap_boundaries([3.4], 60) == [3.4]


def test_batida_cortes_na_grade():
    novas = music.snap_boundaries([2.9, 3.2, 3.1], 100)
    beat = music.beat_seconds(100)
    for corte in music.cut_times(novas):
        assert abs(corte / beat - round(corte / beat)) < 0.01


def test_musica_auto_liga_sem_voz_e_desliga_com_voz():
    assert music.is_on("auto", False) and not music.is_on("auto", True)
    assert music.is_on("on", True) and not music.is_on("off", False)


def test_modo_invalido():
    with pytest.raises(ReelError, match="--music"):
        music.validate("tocar")


def test_ducking_com_voz_usa_sidechain():
    filtro, rotulo = music.duck_filter(True, 2, "[aout]")
    assert "sidechaincompress" in filtro and rotulo == "[mix]"
    assert "sidechaincompress" not in music.duck_filter(False, 1, "")[0]
