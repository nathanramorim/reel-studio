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


def _plan(transcript, clip, overlays=True):
    from pathlib import Path

    from reel_studio.core.cut import plan
    theme = contracts.load_theme("forge")
    return plan(Path("v.mp4"), Path("w"), {"clips": [clip]}, transcript, theme,
                size=(1920, 1080), layout="fill", duration=60.0, overlays=overlays)[0]


CLIP = {"id": "clip-01", "start": 1.0, "end": 5.0, "hook": "Gancho do corte"}
HOOK_OVERLAY = {"type": "hook", "at": 0.0, "text": "Gancho do overlay"}


def test_hook_duplicado_overlay_hook_suprime_o_do_corte(transcript):
    job = _plan(transcript, {**CLIP, "overlays": [HOOK_OVERLAY]})
    assert "Gancho do corte" not in job.ass_text


def test_hook_duplicado_sem_overlay_hook_mantem_o_do_corte(transcript):
    assert "Gancho do corte" in _plan(transcript, CLIP).ass_text
    outro = {**CLIP, "overlays": [{"type": "cta", "at": 1.0}]}
    assert "Gancho do corte" in _plan(transcript, outro).ass_text


def test_hook_duplicado_overlays_desligados_mantem_o_do_corte(transcript):
    job = _plan(transcript, {**CLIP, "overlays": [HOOK_OVERLAY]}, overlays=False)
    assert "Gancho do corte" in job.ass_text
