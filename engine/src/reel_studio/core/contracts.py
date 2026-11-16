"""Validação dos JSON contra os schemas de contracts/ (fonte única, DUP-04)."""

from __future__ import annotations

from functools import cache
from pathlib import Path

from jsonschema import Draft202012Validator

from . import paths
from .errors import ContractError

BRAND_ASSETS = ("logo", "mascot")

KINDS = ("transcript", "clips", "scenes", "theme", "style")


@cache
def _validator(kind: str) -> Draft202012Validator:
    if kind not in KINDS:
        raise ValueError(f"contrato desconhecido: {kind}")
    schema = paths.read_json(paths.contracts_dir() / f"{kind}.schema.json")
    return Draft202012Validator(schema)


def check_overlays(clips: dict) -> None:
    """Cada overlay cabe na duração do corte (`at` e `dur` são relativos ao corte)."""
    for clip in clips["clips"]:
        length = clip["end"] - clip["start"]
        for i, o in enumerate(clip.get("overlays", []), 1):
            if o["at"] + o["dur"] > length + 1e-6:
                raise ContractError(
                    f"{clip['id']}: overlay {i} ({o['type']}) termina em "
                    f"{o['at'] + o['dur']:.2f}s, fora do corte de {length:.2f}s.")


def validate(kind: str, data: dict) -> dict:
    errors = sorted(_validator(kind).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        lines = [f"  {'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}" for e in errors[:5]]
        raise ContractError(f"{kind} fora do contrato:\n" + "\n".join(lines))
    if kind == "clips":
        check_overlays(data)
    return data


def load(kind: str, path: Path) -> dict:
    return validate(kind, paths.read_json(path))


def resolve_brand(theme: dict, folder: Path) -> dict:
    """Ativos do `brand` viram caminhos absolutos, confinados à pasta do tema (SEG-02)."""
    brand = theme.get("brand")
    if not brand:
        return theme
    root = folder.resolve()
    resolved = dict(brand)
    for key in BRAND_ASSETS:
        rel = brand.get(key)
        if not rel:
            continue
        target = (root / rel).resolve()
        if not target.is_relative_to(root):
            raise ContractError(f"Tema {theme['id']}: brand.{key} sai da pasta do tema ({rel}).")
        if not target.is_file():
            raise ContractError(f"Tema {theme['id']}: brand.{key} não encontrado ({rel}).")
        resolved[key] = str(target)
    return {**theme, "brand": resolved}


def load_theme(theme_id: str) -> dict:
    path = paths.theme_path(theme_id)
    theme = load("theme", path)
    return resolve_brand(theme, path.parent / theme["id"])


def load_style(style_id: str) -> dict:
    return load("style", paths.style_path(style_id))
