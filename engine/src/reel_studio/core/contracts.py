"""Validação dos JSON contra os schemas de contracts/ (fonte única, DUP-04)."""

from __future__ import annotations

from functools import cache
from pathlib import Path

from jsonschema import Draft202012Validator

from . import paths
from .errors import ContractError

KINDS = ("transcript", "clips", "scenes", "theme", "style")


@cache
def _validator(kind: str) -> Draft202012Validator:
    if kind not in KINDS:
        raise ValueError(f"contrato desconhecido: {kind}")
    schema = paths.read_json(paths.contracts_dir() / f"{kind}.schema.json")
    return Draft202012Validator(schema)


def validate(kind: str, data: dict) -> dict:
    errors = sorted(_validator(kind).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        lines = [f"  {'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}" for e in errors[:5]]
        raise ContractError(f"{kind} fora do contrato:\n" + "\n".join(lines))
    return data


def load(kind: str, path: Path) -> dict:
    return validate(kind, paths.read_json(path))


def load_theme(theme_id: str) -> dict:
    return load("theme", paths.theme_path(theme_id))


def load_style(style_id: str) -> dict:
    return load("style", paths.style_path(style_id))
