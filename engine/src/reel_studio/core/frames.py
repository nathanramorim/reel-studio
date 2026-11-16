"""Análise de quadros: rosto e região com atividade. OpenCV é opcional (extra vision, ARQ-04)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SAMPLES = 8
MIN_FACE_HEIGHT = 0.08   # rosto com pelo menos 8% da altura do quadro
MIN_FACE_SHARE = 0.5     # presente em pelo menos metade dos quadros
MAX_REGION_AREA = 0.6    # atividade além disso é "espalhada"
MIN_ACTIVE_PIXELS = 0.001
DIFF_THRESHOLD = 25
MARGIN = 0.08
MIN_REGION_WIDTH = 0.35


@dataclass(frozen=True)
class Region:
    """Retângulo normalizado (0 a 1) sobre o quadro."""
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class Analysis:
    face_x: float | None = None     # centro horizontal do rosto, 0 a 1
    region: Region | None = None    # atividade concentrada


def _expand(x0: float, y0: float, x1: float, y1: float) -> Region:
    w = min(1.0, max(x1 - x0 + 2 * MARGIN, MIN_REGION_WIDTH))
    h = min(1.0, y1 - y0 + 2 * MARGIN)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x = min(max(cx - w / 2, 0.0), 1.0 - w)
    y = min(max(cy - h / 2, 0.0), 1.0 - h)
    return Region(x, y, w, h)


def analyze(video: Path, start: float, end: float) -> Analysis | None:
    """Amostra quadros do trecho. None quando o OpenCV não está instalado."""
    try:
        import cv2
    except ImportError:
        return None
    cap = cv2.VideoCapture(str(video))
    try:
        frames = []
        for i in range(SAMPLES):
            t = start + (end - start) * (i + 0.5) / SAMPLES
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = cap.read()
            if ok:
                frames.append(frame)
    finally:
        cap.release()
    if len(frames) < 2:
        return Analysis()
    return _analyze_frames(cv2, frames)


def _analyze_frames(cv2, frames: list) -> Analysis:
    height, width = frames[0].shape[:2]
    scale = 480 / max(width, height)
    small = [cv2.cvtColor(cv2.resize(f, None, fx=scale, fy=scale), cv2.COLOR_BGR2GRAY)
             for f in frames]
    face_x = _face(cv2, small)
    if face_x is not None:
        return Analysis(face_x=face_x)
    return Analysis(region=_activity(cv2, small))


def _face(cv2, gray: list) -> float | None:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    xs = []
    for g in gray:
        h, w = g.shape
        found = cascade.detectMultiScale(g, 1.1, 5, minSize=(int(h * MIN_FACE_HEIGHT),) * 2)
        if len(found):
            fx, _, fw, _ = max(found, key=lambda r: r[2] * r[3])
            xs.append((fx + fw / 2) / w)
    if len(xs) < len(gray) * MIN_FACE_SHARE:
        return None
    return sorted(xs)[len(xs) // 2]


def _activity(cv2, gray: list) -> Region | None:
    h, w = gray[0].shape
    mask = None
    for a, b in zip(gray, gray[1:], strict=False):
        d = (cv2.absdiff(a, b) > DIFF_THRESHOLD).astype("uint8")
        mask = d if mask is None else mask | d
    if mask.mean() < MIN_ACTIVE_PIXELS:
        return None
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15)))
    x, y, bw, bh = cv2.boundingRect(mask)
    region = _expand(x / w, y / h, (x + bw) / w, (y + bh) / h)
    if region.w * region.h > MAX_REGION_AREA:
        return None
    return region
