"""Onde ficam contratos, temas e estilos (fonte única de caminhos)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .errors import ReelError


def repo_root() -> Path:
    env = os.environ.get("REEL_STUDIO_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # engine/src/reel_studio/core/paths.py -> raiz do repositório
    return Path(__file__).resolve().parents[4]


def user_dir() -> Path:
    """Temas e estilos da pessoa usuária, fora do plugin."""
    return Path(os.environ.get("REEL_STUDIO_HOME", "~/.config/reel-studio")).expanduser()


def contracts_dir() -> Path:
    return repo_root() / "contracts"


def render_dir() -> Path:
    return repo_root() / "render"


def _theme_dirs() -> list[Path]:
    return [user_dir() / "themes", repo_root() / "themes"]


def _style_dirs() -> list[Path]:
    return [user_dir() / "styles", repo_root() / "styles"]


def list_themes() -> list[str]:
    ids = {p.stem for d in _theme_dirs() if d.is_dir() for p in d.glob("*.json")}
    return sorted(ids)


def list_styles() -> list[str]:
    ids = {p.parent.name for d in _style_dirs() if d.is_dir() for p in d.glob("*/style.json")}
    return sorted(ids)


def theme_path(theme_id: str) -> Path:
    for d in _theme_dirs():
        p = d / f"{theme_id}.json"
        if p.is_file():
            return p
    raise ReelError(f"Tema '{theme_id}' não encontrado. Disponíveis: {', '.join(list_themes())}")


def style_path(style_id: str) -> Path:
    for d in _style_dirs():
        p = d / style_id / "style.json"
        if p.is_file():
            return p
    raise ReelError(f"Estilo '{style_id}' não encontrado. Disponíveis: {', '.join(list_styles())}")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ReelError(f"Arquivo não encontrado: {path}") from e
    except json.JSONDecodeError as e:
        raise ReelError(f"JSON inválido em {path}: {e}") from e


def write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
