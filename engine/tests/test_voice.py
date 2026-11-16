import math
import struct
import wave

import pytest

from reel_studio.core import voice
from reel_studio.core.errors import ReelError


def _wav(path, seconds, amp=8000, rate=16000, noise=0):
    frames = []
    for n in range(int(seconds * rate)):
        v = amp * math.sin(2 * math.pi * 220 * n / rate) if amp else 0
        frames.append(int(v + (noise if n % 2 else -noise)))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack(f"<{len(frames)}h", *frames))
    return path


def _segs(*spans):
    return [{"start": a, "end": b, "text": "x"} for a, b in spans]


def test_amostra_respeita_10_a_30s():
    for a, b in voice.candidates(_segs((0, 6), (6.2, 14), (14.3, 60))):
        assert voice.MIN_REF <= b - a <= voice.MAX_REF


def test_amostra_so_fala_continua():
    # pausa de 5 s entre os dois blocos: nenhum bloco tem 10 s sozinho
    assert voice.candidates(_segs((0, 6), (11, 17))) == []


def test_amostra_sem_sobreposicao():
    # (0,8) e (6,14) se sobrepõem: juntos dariam 14 s, mas nenhum vira amostra sozinho
    assert voice.candidates(_segs((0, 8), (6, 14))) == []


def test_amostra_escolhe_a_mais_limpa(tmp_path):
    ruidoso = _wav(tmp_path / "a.wav", 12, noise=6000)
    limpo = _wav(tmp_path / "b.wav", 12, noise=0)
    assert voice.snr_db(limpo, 0, 12) >= voice.snr_db(ruidoso, 0, 12)


def test_amostra_sem_trecho_levanta_erro(tmp_path):
    audio = _wav(tmp_path / "a.wav", 6)
    with pytest.raises(ReelError, match="fala contínua"):
        voice.pick_window({"segments": _segs((0, 5))}, audio)


def test_amostra_escolhe_o_trecho(tmp_path):
    audio = _wav(tmp_path / "a.wav", 40)
    a, b = voice.pick_window({"segments": _segs((0, 12), (30, 40))}, audio)
    assert 10 <= b - a <= 30


def test_consentimento_exige_a_flag(tmp_path):
    ref = _wav(tmp_path / "ref.wav", 10)
    with pytest.raises(ReelError, match="--confirm-own-voice"):
        voice.require_consent(False, ref)
    assert voice.require_consent(True, ref) == ref


def test_consentimento_sem_referencia_nao_gera_voz():
    with pytest.raises(ReelError, match="--voice-ref"):
        voice.require_consent(True, None)
    with pytest.raises(ReelError, match="--voice-ref"):
        voice.check_consent(True, False)


def test_duracao_segue_o_audio_gerado(tmp_path):
    ref = _wav(tmp_path / "ref.wav", 10)
    chamadas = []

    def sintetizar(texto, referencia, lang, out):
        chamadas.append((texto, lang))
        _wav(out, 2.5 if "um" in texto else 4.0)

    def alinhar(wav):
        return {"segments": [{"start": 0, "end": 1, "text": "x", "words": [
            {"start": 0.1, "end": 0.5, "word": " oi "}, {"start": 0.6, "end": 1.0, "word": "lá"}]}]}

    cenas = [{"narration": "texto um"}, {"narration": "texto dois"}]
    v = voice.synthesize(cenas, ref, "pt", tmp_path, sintetizar, alinhar)
    assert v.durations == [2.5, 4.0]
    assert v.words[0][0] == {"word": "oi", "start": 0.1, "end": 0.5}
    assert voice.wav_seconds(v.joined) == pytest.approx(6.5, abs=0.01)
    assert chamadas == [("texto um", "pt"), ("texto dois", "pt")]


def test_duracao_cena_sem_narracao_falha(tmp_path):
    with pytest.raises(ReelError, match="sem `narration`"):
        voice.synthesize([{"narration": ""}], tmp_path / "r.wav", "pt", tmp_path,
                         lambda *a: None, lambda w: {"segments": []})
