"""Não regressão (05): sem camadas, corte e legenda ficam idênticos aos anteriores."""

import hashlib
from pathlib import Path

from reel_studio.core.captions import build_ass
from reel_studio.core.contracts import load_theme
from reel_studio.core.cut import ffmpeg_args

CORTE = [
    "ffmpeg", "-y", "-loglevel", "error", "-ss", "1.00", "-t", "3.00", "-i", "v.mp4", "-vf",
    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)*0.5000:0,"
    "ass=clip-01.ass,fade=t=in:d=0.25,fade=t=out:st=2.55:d=0.45",
    "-af", "afade=t=in:d=0.25,afade=t=out:st=2.55:d=0.45",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart", "out.mp4",
]
ASS_SHA256 = "fc1fbdfa926f1d2ac5a9fdd1eaad0d755e7a76b8fd4a4c21a94cb50cb2fccd8d"


def test_regressao_comando_do_corte_sem_camadas():
    assert ffmpeg_args("ffmpeg", Path("v.mp4"), 1.0, 4.0, "clip-01.ass", Path("out.mp4")) == CORTE


def test_regressao_ass_do_corte_sem_camadas(transcript):
    ass = build_ass(transcript, 0.0, 3.2, load_theme("forge"), "Gancho")
    assert hashlib.sha256(ass.encode()).hexdigest() == ASS_SHA256
