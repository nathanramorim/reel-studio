"""Análise de quadros: rosto e região com atividade. OpenCV é opcional (extra vision, ARQ-04)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

WINDOW_SAMPLES = 4       # quadros por janela de tempo
WINDOW_SECONDS = 6.0     # duração alvo de cada janela
MAX_WINDOWS = 6
SHIFT = 0.08             # deslocamento do centro (fração do quadro) que justifica trocar a região
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
    region: Region | None = None    # atividade concentrada (primeira região da sequência)
    steps: tuple[tuple[float, Region], ...] = ()  # (t relativo ao corte, região) por troca


def _expand(x0: float, y0: float, x1: float, y1: float) -> Region:
    w = min(1.0, max(x1 - x0 + 2 * MARGIN, MIN_REGION_WIDTH))
    h = min(1.0, y1 - y0 + 2 * MARGIN)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x = min(max(cx - w / 2, 0.0), 1.0 - w)
    y = min(max(cy - h / 2, 0.0), 1.0 - h)
    return Region(x, y, w, h)


def track(regions: list[Region | None], starts: list[float]) -> tuple[tuple[float, Region], ...]:
    """Sequência de trocas: só muda de região quando o centro se afasta o bastante (histerese)."""
    steps: list[tuple[float, Region]] = []
    for t, r in zip(starts, regions, strict=True):
        if r is None:
            continue
        if not steps:
            steps.append((0.0, r))
            continue
        prev = steps[-1][1]
        if (abs((r.x + r.w / 2) - (prev.x + prev.w / 2)) >= SHIFT
                or abs((r.y + r.h / 2) - (prev.y + prev.h / 2)) >= SHIFT):
            steps.append((t, r))
    return tuple(steps)


def analyze(video: Path, start: float, end: float) -> Analysis | None:
    """Amostra quadros do trecho. None quando o OpenCV não está instalado."""
    try:
        import cv2
    except ImportError:
        return None
    cap = cv2.VideoCapture(str(video))
    try:
        frames = []
        total = _window_count(end - start) * WINDOW_SAMPLES
        for i in range(total):
            t = start + (end - start) * (i + 0.5) / total
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = cap.read()
            if ok:
                frames.append(frame)
    finally:
        cap.release()
    if len(frames) < 2:
        return Analysis()
    return _analyze_frames(cv2, frames, end - start)


def _window_count(duration: float) -> int:
    return min(MAX_WINDOWS, max(1, round(duration / WINDOW_SECONDS)))


def _analyze_frames(cv2, frames: list, duration: float = 0.0) -> Analysis:
    height, width = frames[0].shape[:2]
    scale = 480 / max(width, height)
    small = [cv2.cvtColor(cv2.resize(f, None, fx=scale, fy=scale), cv2.COLOR_BGR2GRAY)
             for f in frames]
    face_x = _face(cv2, small)
    if face_x is not None:
        return Analysis(face_x=face_x)
    n = max(1, len(small) // WINDOW_SAMPLES)
    size = len(small) // n
    groups = [small[i * size:(i + 1) * size] for i in range(n)]
    starts = [duration * i / n for i in range(n)]
    steps = track([_activity(cv2, g) if len(g) > 1 else None for g in groups], starts)
    return Analysis(region=steps[0][1] if steps else None, steps=steps)


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
