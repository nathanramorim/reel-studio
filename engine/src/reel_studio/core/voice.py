"""Voz gerada a partir da gravação (clone local, extra `tts`). Nada sai da máquina (SEG-05).

O modelo entra por import tardio e é baixado uma vez, na instalação do extra, nunca no render.
A marca d'água do modelo é mantida. Amostra e áudio ficam na pasta do vídeo.
"""

from __future__ import annotations

import array
import math
import wave
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from . import proc
from .errors import ReelError

MIN_REF, MAX_REF = 10.0, 30.0
MAX_GAP = 0.6
REF_NAME = "voice-ref.wav"
VOICE_NAME = "voice-generated.wav"

Synth = Callable[[str, Path, str, Path], None]
Align = Callable[[Path], dict]


@dataclass(frozen=True)
class Voice:
    """Voz gerada: um áudio por cena, a duração de cada um e as palavras com tempo."""

    files: list[Path]
    durations: list[float]
    words: list[list[dict]]
    joined: Path


def check_consent(confirmed: bool, has_ref: bool) -> None:
    """Sem referência, sem voz; sem a confirmação de que a voz é própria (ou autorizada), erro."""
    if not has_ref:
        raise ReelError("--voice clone exige --voice-ref: sem referência, sem voz.")
    if not confirmed:
        raise ReelError("--voice clone exige --confirm-own-voice: confirme que a voz é sua "
                        "ou que você tem autorização para cloná-la.")


def require_consent(confirmed: bool, ref: Path | None) -> Path:
    """Consentimento e arquivo de referência existente."""
    check_consent(confirmed, ref is not None)
    if ref is None or not ref.is_file():
        raise ReelError(f"Referência de voz não encontrada: {ref}")
    return ref


def snr_db(wav: Path, start: float, end: float) -> float:
    """Relação sinal-ruído estimada: fala (RMS da janela) contra o piso (10% mais baixos)."""
    with wave.open(str(wav), "rb") as w:
        rate, ch = w.getframerate(), w.getnchannels()
        w.setpos(min(int(start * rate), w.getnframes()))
        raw = w.readframes(int((end - start) * rate))
    data = array.array("h")
    data.frombytes(raw[: len(raw) // 2 * 2])
    mono = data[::ch] if ch > 1 else data
    step = max(1, rate // 50)
    rms = []
    for i in range(0, len(mono) - step, step):
        frame = mono[i:i + step]
        rms.append(math.sqrt(sum(x * x for x in frame) / len(frame)))
    if len(rms) < 10:
        return 0.0
    rms.sort()
    floor = max(sum(rms[: max(1, len(rms) // 10)]) / max(1, len(rms) // 10), 1.0)
    speech = max(sum(rms[-len(rms) // 2:]) / (len(rms) // 2), 1.0)
    return 20 * math.log10(speech / floor)


def _runs(segments: list[dict]) -> list[list[dict]]:
    """Trechos de fala contínua: segmentos seguidos com pausa curta e sem sobreposição."""
    runs: list[list[dict]] = []
    for seg in sorted(segments, key=lambda s: s["start"]):
        prev = runs[-1][-1] if runs else None
        if prev and prev["end"] > seg["start"]:
            runs.append([])  # sobreposição: o trecho recomeça depois
            runs[-1].append(seg)
        elif prev and seg["start"] - prev["end"] <= MAX_GAP:
            runs[-1].append(seg)
        else:
            runs.append([seg])
    return runs


def candidates(segments: list[dict]) -> list[tuple[float, float]]:
    """Janelas de 10 a 30 s de fala contínua, cortadas em limites de segmento."""
    out = []
    for run in _runs(segments):
        for i in range(len(run)):
            end = run[i]["start"]
            for seg in run[i:]:
                if seg["end"] - run[i]["start"] > MAX_REF:
                    break
                end = seg["end"]
            if end - run[i]["start"] >= MIN_REF:
                out.append((run[i]["start"], end))
    return out


def pick_window(transcript: dict, audio: Path) -> tuple[float, float]:
    """Melhor amostra: entre as janelas contínuas, a de maior relação sinal-ruído."""
    options = candidates(transcript["segments"])
    if not options:
        raise ReelError(f"Sem trecho de fala contínua de {MIN_REF:.0f} a {MAX_REF:.0f} s "
                        "para servir de referência de voz. Passe --voice-ref com uma amostra.")
    return max(options, key=lambda w: snr_db(audio, *w))


def reference_args(ffmpeg: str, audio: Path, window: tuple[float, float], out: Path) -> list[str]:
    start, end = window
    return [ffmpeg, "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
            "-i", str(audio), "-ac", "1", "-ar", "24000", str(out)]


def reference(transcript: dict, audio: Path, workdir: Path) -> Path:
    """Extrai a melhor amostra da gravação para `voice-ref.wav`, na pasta do vídeo."""
    window = pick_window(transcript, audio)
    out = workdir / REF_NAME
    proc.run(reference_args(proc.require_bin("ffmpeg", proc.FFMPEG_HINT), audio, window, out))
    return out


def wav_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def join_wavs(files: list[Path], out: Path) -> Path:
    """Emenda os áudios das cenas (mesmo formato) num só `.wav`."""
    with wave.open(str(files[0]), "rb") as first:
        params = first.getparams()
    with wave.open(str(out), "wb") as dst:
        dst.setparams(params)
        for f in files:
            with wave.open(str(f), "rb") as src:
                if src.getparams()[:3] != params[:3] or src.getframerate() != params.framerate:
                    raise ReelError("Os áudios gerados têm formatos diferentes.")
                dst.writeframes(src.readframes(src.getnframes()))
    return out


def chatterbox_synth(lang: str) -> Synth:
    """Sintetizador real (extra `tts`): import tardio, dispositivo automático."""
    try:
        import torch
        import torchaudio
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    except ImportError as e:
        raise ReelError("Voz gerada precisa do extra 'tts': uv sync --extra tts") from e
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)

    def run(text: str, ref: Path, language: str, out: Path) -> None:
        wav = model.generate(text, language_id=language or lang, audio_prompt_path=str(ref))
        torchaudio.save(str(out), wav, model.sr)

    return run


def synthesize(scenes: list[dict], ref: Path, lang: str, workdir: Path, synth: Synth,
               align: Align) -> Voice:
    """Um áudio por cena; a cena dura o áudio gerado e as palavras vêm da transcrição dele."""
    files, durs, words = [], [], []
    for i, scene in enumerate(scenes):
        text = scene.get("narration", "").strip()
        if not text:
            raise ReelError(f"Cena {i + 1} sem `narration`: não há o que falar com --voice clone.")
        out = workdir / f"voice-scene-{i + 1:02d}.wav"
        synth(text, ref, lang, out)
        files.append(out)
        durs.append(round(wav_seconds(out), 3))
        transcript = align(out)
        words.append([{"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
                      for seg in transcript["segments"]
                      for w in (seg.get("words") or []) if w["word"].strip()])
    return Voice(files, durs, words, join_wavs(files, workdir / VOICE_NAME))
