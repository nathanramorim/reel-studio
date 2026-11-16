"""Glossário: corrige em memória termos que o Whisper erra (frase errada -> frase certa)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .errors import ReelError

FILE_NAME = "correcoes.json"
MAX_BYTES = 256 * 1024
MAX_ENTRIES = 2000
_NON_WORD = re.compile(r"[\W_]+")
_TRAIL = re.compile(r"[^\w]+$")


@dataclass(frozen=True)
class Glossary:
    mapping: dict[str, str]
    source: str


def _norm(word: str) -> str:
    return _NON_WORD.sub("", word.casefold())


def _clean(raw: object, origin: str) -> dict[str, str]:
    """Valida o mapa e expande chaves com variantes (`a|b|c`) em uma entrada por variante."""
    if not isinstance(raw, dict):
        raise ReelError(f"Glossário inválido em {origin}: esperado um objeto JSON.")
    out: dict[str, str] = {}
    seen: dict[str, tuple[str, str]] = {}
    for key, value in raw.items():
        if not isinstance(value, str):
            raise ReelError(f"Glossário inválido em {origin}: '{key}' deve ser texto.")
        if key.startswith("_"):
            continue
        for variant in (v.strip() for v in key.split("|")):
            norm = "".join(_norm(p) for p in variant.split())
            if not norm:
                continue
            prev = seen.get(norm)
            if prev and prev[1] != value.strip():
                raise ReelError(f"Glossário inválido em {origin}: a variante '{variant}' "
                                f"tem dois valores ('{prev[1]}' e '{value.strip()}').")
            seen[norm] = (variant, value.strip())
            out[variant] = value
    if len(out) > MAX_ENTRIES:
        raise ReelError(f"Glossário grande demais em {origin}: máximo {MAX_ENTRIES} variantes.")
    return out


def load(path: Path) -> dict[str, str]:
    """Lê e valida um correcoes.json (só leitura, com limite de tamanho)."""
    try:
        size = path.stat().st_size
    except OSError as e:
        raise ReelError(f"Glossário não encontrado: {path}") from e
    if size > MAX_BYTES:
        raise ReelError(f"Glossário grande demais em {path}: máximo {MAX_BYTES // 1024} KB.")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ReelError(f"Glossário inválido em {path}: {e}") from e
    return _clean(raw, str(path))


def _search_dirs(video_dir: Path) -> list[Path]:
    dirs = []
    for d in (video_dir, *video_dir.parents):
        dirs.append(d)
        if (d / ".git").exists():
            break
    else:
        return [video_dir]
    return dirs


def find(video: Path, workdir: Path, theme: dict, explicit: Path | None = None) -> Glossary | None:
    """Acha o glossário mais específico: --glossary, pastas do vídeo, trabalho, tema."""
    if explicit is not None:
        return Glossary(load(explicit), str(explicit))
    candidates = [d / FILE_NAME for d in _search_dirs(video.resolve().parent)]
    candidates.append(workdir / FILE_NAME)
    for c in candidates:
        if c.is_file():
            return Glossary(load(c), str(c))
    if theme.get("glossary"):
        return Glossary(_clean(theme["glossary"], f"tema {theme.get('id', '?')}"),
                        f"tema {theme.get('id', '?')}")
    return None


def _index(mapping: dict[str, str]) -> tuple[dict[str, str], int]:
    table: dict[str, str] = {}
    longest = 1
    for wrong, right in mapping.items():
        parts = wrong.split()
        key = "".join(_norm(p) for p in parts)
        if key and right.strip():
            table[key] = right.strip()
            longest = max(longest, len(parts))
    return table, longest


def _match(tokens: list[str], table: dict[str, str], longest: int) -> list[tuple[int, int, str]]:
    """Trechos (início, fim exclusivo, texto novo); frase mais longa primeiro, sem reaplicar."""
    spans, i = [], 0
    while i < len(tokens):
        for n in range(min(longest, len(tokens) - i), 0, -1):
            key = "".join(_norm(t) for t in tokens[i:i + n])
            if key and key in table:
                spans.append((i, i + n, table[key]))
                i += n
                break
        else:
            i += 1
    return spans


def _timed(words: list[dict], spans: list[tuple[int, int, str]]) -> list[dict]:
    out, pos = [], 0
    for a, b, new in spans:
        out.extend(words[pos:a])
        first, last = words[a], words[b - 1]
        pieces = new.split()
        tail = _TRAIL.search(last["word"].strip())
        weights = [len(p) for p in pieces]
        total, t = sum(weights), first["start"]
        for k, (piece, wgt) in enumerate(zip(pieces, weights, strict=True)):
            span = (last["end"] - first["start"]) * wgt / total
            end = last["end"] if k == len(pieces) - 1 else t + span
            word = piece + (tail.group() if tail and k == len(pieces) - 1 else "")
            out.append({**first, "start": t, "end": end, "word": word})
            t = end
        pos = b
    out.extend(words[pos:])
    return out


def _text(text: str, spans: list[tuple[int, int, str]]) -> str:
    tokens, out, pos = text.split(), [], 0
    for a, b, new in spans:
        out.extend(tokens[pos:a])
        tail = _TRAIL.search(tokens[b - 1])
        out.append(new + (tail.group() if tail else ""))
        pos = b
    out.extend(tokens[pos:])
    return " ".join(out)


def apply(transcript: dict, mapping: dict[str, str]) -> tuple[dict, int]:
    """Devolve cópia da transcrição corrigida e o nº de correções (o original não muda)."""
    table, longest = _index(mapping)
    count, segments = 0, []
    for seg in transcript["segments"]:
        new = dict(seg)
        words = seg.get("words")
        if words:
            spans = _match([w["word"] for w in words], table, longest)
            if spans:
                new["words"] = _timed(words, spans)
                count += len(spans)
        text_spans = _match(seg["text"].split(), table, longest)
        if text_spans:
            new["text"] = _text(seg["text"], text_spans)
            if not words:
                count += len(text_spans)
        segments.append(new)
    return {**transcript, "segments": segments}, count
