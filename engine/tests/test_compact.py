from reel_studio.core.compact import compact, estimate_tokens


def test_compact_tem_um_segmento_por_linha(transcript):
    out = compact(transcript)
    assert out.count("\n") == len(transcript["segments"]) - 1
    assert "[0.0]" in out
    assert "automatizar" in out


def test_compact_recorta_por_janela(transcript):
    out = compact(transcript, start=3.5, end=8.0)
    assert "Hoje eu vou" not in out
    assert "extrair o áudio" in out


def test_estimate_tokens_cresce_com_texto():
    assert estimate_tokens("a" * 400) > estimate_tokens("a" * 40)
