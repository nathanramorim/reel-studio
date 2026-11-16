"""Trilha e efeitos sintetizados com a biblioteca padrão, na grade de batidas (ARQ-04).

Determinístico (semente fixa): a mesma entrada gera o mesmo `.wav`. Baixo, harmonia e um
chiado leve por batida; um efeito suave em cada corte. Tudo contado do quadro 0.
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from . import tone
from .errors import ReelError

RATE = 22050
SNAP = 0.25
SEED = 20260516
MUSIC = ("auto", "on", "off")
GAIN = 0.35
# Progressão (graus em semitons acima da tônica) por compasso de 4 batidas.
PROGRESSION = ((0, 4, 7), (5, 9, 12), (7, 11, 14), (3, 7, 10))
ROOT_HZ = 110.0  # lá


def validate(mode: str) -> str:
    if mode not in MUSIC:
        raise ReelError(f"--music aceita {', '.join(MUSIC)}; recebi {mode!r}.")
    return mode


def is_on(mode: str, has_voice: bool) -> bool:
    """`auto` liga sem voz e desliga com voz; `on` e `off` são explícitos."""
    return mode == "on" or (mode == "auto" and not has_voice)


def beat_seconds(bpm: int) -> float:
    return 60.0 / bpm


def snap_boundaries(durations: list[float], bpm: int, tolerance: float = SNAP) -> list[float]:
    """Cada limite de cena vai para a batida mais próxima se estiver a até `tolerance` s.

    Devolve as novas durações (mesma soma de limites encaixados; nunca abaixo de 1 s).
    """
    beat = beat_seconds(bpm)
    edges, acc = [], 0.0
    for d in durations:
        acc += d
        edges.append(acc)
    snapped, prev = [], 0.0
    for e in edges:
        nearest = round(e / beat) * beat
        cand = nearest if abs(nearest - e) <= tolerance else e
        if cand - prev < 1.0:
            cand = e
        snapped.append(cand)
        prev = cand
    return [round(b - a, 3) for a, b in zip([0.0, *snapped[:-1]], snapped, strict=True)]


def cut_times(durations: list[float]) -> list[float]:
    """Instantes dos cortes (fim de cada cena menos a última)."""
    out, acc = [], 0.0
    for d in durations[:-1]:
        acc += d
        out.append(round(acc, 3))
    return out


def plan(durations: list[float], tone_id: str | None) -> dict:
    """Plano da trilha (usado no `--dry-run`, que não escreve nada)."""
    bpm = tone.bpm(tone_id)
    return {"bpm": bpm, "length": round(sum(durations), 3), "cuts": cut_times(durations)}


class _Noise:
    """Gerador congruencial linear: ruído reproduzível sem `random`."""

    def __init__(self, seed: int):
        self.state = seed

    def next(self) -> float:
        self.state = (self.state * 1664525 + 1013904223) % 2**32
        return self.state / 2**31 - 1.0


def _tone(freq: float, t: float, harmonics: int = 2) -> float:
    return sum(math.sin(2 * math.pi * freq * (k + 1) * t) / (k + 1) for k in range(harmonics))


def samples(length: float, bpm: int, cuts: list[float]) -> list[int]:
    """Amostras PCM 16 bits mono: baixo na batida, acorde por compasso, chiado e efeitos."""
    total = round(length * RATE)
    beat = beat_seconds(bpm)
    noise = _Noise(SEED)
    out = [0] * total
    for n in range(total):
        t = n / RATE
        idx = int(t / beat)
        local = t - idx * beat
        chord = PROGRESSION[(idx // 4) % len(PROGRESSION)]
        bass_env = math.exp(-local * 5)
        v = 0.45 * bass_env * _tone(ROOT_HZ * 2 ** (chord[0] / 12) / 2, local)
        pad = sum(math.sin(2 * math.pi * ROOT_HZ * 2 ** ((d + 12) / 12) * t) for d in chord) / 9
        v += pad * (0.6 + 0.4 * math.sin(2 * math.pi * t / (beat * 8)))
        v += 0.05 * noise.next() * math.exp(-local * 40) * (1 if idx % 2 else 0.4)
        out[n] = int(max(-1.0, min(1.0, v * GAIN)) * 32767)
    for c in cuts:
        start = round(c * RATE)
        for k in range(min(round(0.18 * RATE), total - start)):
            t = k / RATE
            sweep = 600 + 2200 * (t / 0.18)
            fx = 0.22 * math.sin(2 * math.pi * sweep * t) * math.exp(-t * 18)
            out[start + k] = max(-32767, min(32767, out[start + k] + int(fx * 32767 * GAIN)))
    return out


def write_wav(path: Path, length: float, bpm: int, cuts: list[float]) -> Path:
    data = samples(length, bpm, cuts)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(struct.pack(f"<{len(data)}h", *data))
    return path


def duck_filter(has_voice: bool, music_index: int, voice_label: str) -> tuple[str, str]:
    """Filtro da mixagem e o rótulo da saída de áudio.

    Com voz: `sidechaincompress` abaixa a trilha quando a voz fala. Sem voz: trilha com ganho.
    """
    m = f"[{music_index}:a]"
    if not has_voice:
        return f"{m}volume=0.8[mix]", "[mix]"
    return (f"{voice_label}asplit=2[v1][v2];{m}volume=0.6[m];"
            "[m][v1]sidechaincompress=threshold=0.04:ratio=10:attack=20:release=400[md];"
            "[v2][md]amix=inputs=2:duration=first:normalize=0[mix]", "[mix]")
