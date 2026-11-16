"""Paleta do estilo: nomes de token do tema viram hex (o estilo anima, o tema manda nas cores)."""

from __future__ import annotations

from .contrast import HEX, shade

TOKENS = ("bg", "surface", "text", "muted", "accent", "accent2", "success", "warn", "bad")
_DERIVED = (0.0, 0.12, -0.12, 0.22, -0.22)


def derived(accent: str, count: int) -> list[str]:
    """Tons do `accent` para quando o tema não traz o token pedido."""
    return [shade(accent, _DERIVED[i % len(_DERIVED)]) for i in range(count)]


def resolve_color(value: str, colors: dict, fallback: str) -> str:
    """Token do tema -> hex; hex literal passa; token ausente usa `fallback`."""
    if HEX.fullmatch(value):
        return value
    return colors.get(value) or fallback


def resolve(palette: list[str], colors: dict) -> list[str]:
    fallback = derived(colors["accent"], len(palette))
    return [resolve_color(v, colors, fallback[i]) for i, v in enumerate(palette)]
