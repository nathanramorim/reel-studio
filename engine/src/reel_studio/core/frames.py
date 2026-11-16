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
MIN_ACTIVE_PIXELS = 0.001
DIFF_THRESHOLD = 25
BAND_RATIO = 1080 / 920  # proporção da faixa do conteúdo (cut.W / cut.BAND_H)
WIDTH_STEPS = (0.5, 0.67, 0.8)  # larguras candidatas da região (fração do quadro)
MIN_COVERAGE = 0.85      # parte da atividade que a região precisa cobrir
MENU_BAR = 0.03          # topo ignorado (barra de menu)
DOCK = 0.08              # base ignorada (Dock)
MIN_COMPONENT = 0.0005   # componentes menores que isso (fração do quadro) são ruído
MIN_INTERVAL = 3.0       # segundos mínimos entre trocas de região


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


def track(regions: list[Region | None], starts: list[float]) -> tuple[tuple[float, Region], ...]:
    """Sequência de trocas: muda quando o centro se afasta ou o tamanho muda (histerese),
    e nunca antes de MIN_INTERVAL desde a troca anterior."""
    steps: list[tuple[float, Region]] = []
    for t, r in zip(starts, regions, strict=True):
        if r is None:
            continue
        if not steps:
            steps.append((0.0, r))
            continue
        last_t, prev = steps[-1]
        moved = (abs((r.x + r.w / 2) - (prev.x + prev.w / 2)) >= SHIFT
                 or abs((r.y + r.h / 2) - (prev.y + prev.h / 2)) >= SHIFT
                 or abs(r.w - prev.w) > 1e-6)
        if moved and t - last_t >= MIN_INTERVAL:
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
    """Região na proporção da faixa, centrada na densidade da atividade; None se espalhada."""
    h, w = gray[0].shape
    mask = None
    for a, b in zip(gray, gray[1:], strict=False):
        d = (cv2.absdiff(a, b) > DIFF_THRESHOLD).astype("uint8")
        mask = d if mask is None else mask | d
    mask = _drop_edges(mask)
    if mask.mean() < MIN_ACTIVE_PIXELS:
        return None
    mask = _drop_edges(cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))))
    mask = _drop_small(cv2, mask)
    total = int(mask.sum())
    if total == 0:
        return None
    ys, xs = mask.nonzero()
    cx, cy = xs.mean() / w, ys.mean() / h
    max_w = min(1.0, h * BAND_RATIO / w)  # a janela não pode passar da altura do quadro
    for frac in sorted({min(f, max_w) for f in WIDTH_STEPS}):
        rw, rh = frac, frac * w / (BAND_RATIO * h)
        rx = min(max(cx - rw / 2, 0.0), 1.0 - rw)
        ry = min(max(cy - rh / 2, 0.0), 1.0 - rh)
        inside = mask[int(ry * h):int(round((ry + rh) * h)), int(rx * w):int(round((rx + rw) * w))]
        if inside.sum() >= MIN_COVERAGE * total:
            return Region(rx, ry, rw, rh)
    return None


def _drop_edges(mask):
    """Zera a barra de menu (topo) e o Dock (base)."""
    h = mask.shape[0]
    mask = mask.copy()
    mask[:int(h * MENU_BAR)] = 0
    mask[h - int(h * DOCK):] = 0
    return mask


def _drop_small(cv2, mask):
    """Remove componentes isolados menores que MIN_COMPONENT do quadro."""
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] >= MIN_COMPONENT * mask.size]
    import numpy as np
    return np.isin(labels, keep).astype("uint8")
