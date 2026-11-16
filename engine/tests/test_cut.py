from pathlib import Path

from reel_studio.core.contracts import load_theme
from reel_studio.core.cut import ffmpeg_args, plan


def test_ffmpeg_args_corta_e_aplica_legenda():
    args = ffmpeg_args("ffmpeg", Path("v.mp4"), 1.0, 4.0, "clip-01.ass", Path("out.mp4"))
    assert "-ss" in args and "1.00" in args
    assert "-t" in args and "3.00" in args
    assert any("ass=clip-01.ass" in a for a in args)
    assert all(";" not in a and "&&" not in a for a in args)


def test_plan_gera_um_job_por_clip(tmp_path, transcript):
    clips = {"clips": [{"id": "clip-01", "start": 0.0, "end": 3.2, "hook": "x"}]}
    jobs = plan(Path("v.mp4"), tmp_path, clips, transcript, load_theme("pessoal"))
    assert len(jobs) == 1
    assert jobs[0].out.name == "clip-01-pessoal.mp4"
