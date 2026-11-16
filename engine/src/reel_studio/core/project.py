"""Pasta de trabalho por vídeo, com cache invalidado pela impressão digital do arquivo."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from . import paths
from .errors import ReelError

_CHUNK = 4 * 1024 * 1024
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TEXT_ROOT = "reel-projects"
ARTIFACTS = ("audio.wav", "voice.wav", "transcript.json", "clips.json", "scenes.json")


def fingerprint(video: Path) -> str:
    """Hash rápido: tamanho + primeiros e últimos 4 MB."""
    size = video.stat().st_size
    h = hashlib.sha256(str(size).encode())
    with video.open("rb") as f:
        h.update(f.read(_CHUNK))
        if size > _CHUNK:
            f.seek(max(size - _CHUNK, _CHUNK))
            h.update(f.read(_CHUNK))
    return h.hexdigest()[:16]


@dataclass(frozen=True)
class Project:
    video: Path | None
    dir: Path

    @classmethod
    def open(cls, video: str | Path) -> Project:
        v = Path(video).expanduser().resolve()
        if not v.is_file():
            raise ReelError(f"Vídeo não encontrado: {v}")
        d = v.parent / f"{v.stem}.reel"
        d.mkdir(exist_ok=True)
        meta_path = d / "meta.json"
        fp = fingerprint(v)
        meta = paths.read_json(meta_path) if meta_path.is_file() else {}
        if meta.get("fingerprint") != fp:
            for name in ARTIFACTS:
                (d / name).unlink(missing_ok=True)
            paths.write_json(meta_path, {"video": v.name, "fingerprint": fp})
        return cls(video=v, dir=d)

    @classmethod
    def open_text(cls, slug: str, base: str | Path | None = None) -> Project:
        """Pasta de trabalho para conteúdo ou ideia, sem vídeo: `reel-projects/<slug>/`."""
        if not SLUG.fullmatch(slug):
            raise ReelError(f"Nome de projeto inválido: {slug!r}. Use minúsculas, números e hífen.")
        root = (Path(base) if base else Path.cwd()).expanduser().resolve()
        d = root / TEXT_ROOT / slug
        d.mkdir(parents=True, exist_ok=True)
        return cls(video=None, dir=d)

    def path(self, name: str) -> Path:
        return self.dir / name

    @property
    def output(self) -> Path:
        out = self.dir / "output"
        out.mkdir(exist_ok=True)
        return out

    def require(self, name: str, hint: str) -> Path:
        p = self.path(name)
        if not p.is_file():
            raise ReelError(f"Falta {name}. Rode antes: {hint}")
        return p

    def status(self) -> dict[str, bool]:
        return {name: self.path(name).is_file() for name in ARTIFACTS}
