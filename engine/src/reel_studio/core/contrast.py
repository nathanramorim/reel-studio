"""Contraste WCAG 2.x das cores do tema sobre o fundo efetivo (dono do conceito, DUP-01)."""

from __future__ import annotations

import colorsys
import re

from .errors import ReelError

HEX = re.compile(r"#[0-9a-fA-F]{6}")
MIN_TEXT = 4.5
MIN_ACCENT = 3.0
TEXT_COLORS = ("text", "muted")
ACCENT_COLORS = ("accent", "accent2")
_STEP = 0.03


def rgb(color: str) -> tuple[int, int, int]:
    if not HEX.fullmatch(color):
        raise ReelError(f"Cor inválida: {color!r} (esperado #RRGGBB).")
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def to_hex(r: float, g: float, b: float) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, round(v))) for v in (r, g, b)))


def luminance(color: str) -> float:
    def lin(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(v) for v in rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def background_stops(bg: str) -> list[str]:
    """Cores de um fundo sólido ou das paradas de um gradiente CSS."""
    stops = HEX.findall(bg)
    if not stops:
        raise ReelError(f"Fundo sem cor #RRGGBB: {bg!r}.")
    return stops


def worst_ratio(color: str, stops: list[str]) -> float:
    return min(ratio(color, s) for s in stops)


def effective_background(theme: dict, style: dict) -> str:
    """Fundo que de fato aparece: o do estilo `own` ou o do tema."""
    own = style.get("look", {}).get("bg")
    if style.get("background") == "own" and own:
        return own
    return theme["colors"]["bg"]


def shade(color: str, delta: float) -> str:
    """Clareia (delta > 0) ou escurece (delta < 0) mantendo o matiz."""
    h, light, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb(color)))
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, light + delta)), s)
    return to_hex(r * 255, g * 255, b * 255)


def _fix_accent(color: str, stops: list[str], minimum: float) -> str:
    direction = 1 if min(luminance(s) for s in stops) < 0.18 else -1
    out = color
    for _ in range(40):
        if worst_ratio(out, stops) >= minimum:
            return out
        out = shade(out, direction * _STEP)
    return out


def _pick_text(candidates: list[str], stops: list[str], minimum: float,
               ink: str | None = None) -> str:
    """`ink` do estilo vence se contrasta; senão a melhor candidata; por fim preto ou branco."""
    if ink and worst_ratio(ink, stops) >= minimum:
        return ink
    best = max(candidates, key=lambda c: worst_ratio(c, stops))
    if worst_ratio(best, stops) >= minimum:
        return best
    return max(("#000000", "#ffffff"), key=lambda c: worst_ratio(c, stops))


def resolve(theme: dict, style: dict) -> tuple[dict, list[str]]:
    """Tema com `colors` ajustados ao fundo efetivo, mais os nomes das cores ajustadas."""
    colors = dict(theme["colors"])
    stops = background_stops(effective_background(theme, style))
    ink = style.get("look", {}).get("ink")
    pool = [theme["colors"]["bg"], theme["colors"]["text"]]
    changed: list[str] = []
    for name in TEXT_COLORS:
        if worst_ratio(colors[name], stops) < MIN_TEXT:
            colors[name] = _pick_text(pool, stops, MIN_TEXT, ink)
            changed.append(name)
    for name in ACCENT_COLORS:
        if name in colors and worst_ratio(colors[name], stops) < MIN_ACCENT:
            colors[name] = _fix_accent(colors[name], stops, MIN_ACCENT)
            changed.append(name)
    if "text" in changed:
        light = min(luminance(s) for s in stops) > 0.5
        colors["surface"] = shade(stops[0], -0.06 if light else 0.06)
        changed.append("surface")
    return {**theme, "colors": colors}, changed


def ink_for(fills: list[str], theme: dict, style: dict) -> str:
    """Texto sobre as placas: `look.ink` ou a melhor entre o escuro e o claro do tema."""
    ink = style.get("look", {}).get("ink")
    if ink:
        return ink
    return _pick_text([theme["colors"]["bg"], theme["colors"]["text"]], fills, MIN_TEXT)
