"""Tons do roteiro: andamento da trilha e transição padrão (DUP-03: uma tabela só)."""

from __future__ import annotations

from .errors import ContractError

DEFAULT_TONE = "default"
DEFAULT_TRANSITION = "dip"
TRANSITIONS = ("cut", "dip", "wipe", "slide")

# tom -> (BPM, transição padrão)
TONES: dict[str, tuple[int, str]] = {
    "default": (110, "dip"),
    "polished": (100, "dip"),
    "yc-parody": (120, "cut"),
    "chaotic": (120, "wipe"),
    "deadpan": (100, "cut"),
    "cinematic": (100, "slide"),
    "app-store": (110, "slide"),
}


def check(tone: str | None) -> str:
    """Tom conhecido (ou o padrão quando ausente)."""
    chosen = tone or DEFAULT_TONE
    if chosen not in TONES:
        raise ContractError(f"Tom desconhecido: {chosen!r}. Use um de: {', '.join(TONES)}.")
    return chosen


def bpm(tone: str | None) -> int:
    return TONES[check(tone)][0]


def transition(tone: str | None, scene: dict) -> str:
    """Transição da cena: a própria, senão a do tom, senão `dip`."""
    if scene.get("transition"):
        return scene["transition"]
    return TONES[check(tone)][1] if tone else DEFAULT_TRANSITION
