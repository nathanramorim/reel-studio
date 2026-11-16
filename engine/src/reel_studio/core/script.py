"""Modo VSL: reescreve a fala como roteiro curto, em cenas do estilo escolhido."""

from __future__ import annotations

from . import contracts
from .compact import compact
from .errors import ContractError
from .llm import LLMClient

FIELDS = {
    "title": "text",
    "highlight": "text",
    "quote": "text",
    "flow": "steps (2 a 6, até 24 caracteres cada)",
    "list": "items (até 5)",
    "compare": "left e right, cada um {label, points}",
    "chart": "values [{label, value}]",
    "cta": "text",
}


def build_system(style: dict) -> str:
    kinds = "\n".join(f"- {t}: {FIELDS[t]}" for t in style["scene_types"])
    return (
        "Você transforma a transcrição de uma explicação em um roteiro de reel vertical "
        "de 30 a 60 segundos. Corte repetições, mantenha a ideia central e use linguagem simples. "
        f"Use só estes tipos de cena:\n{kinds}\n"
        "Toda cena tem type, dur (segundos) e narration (o que será falado). "
        "Comece com title ou highlight e termine com cta. "
        'Responda só JSON: {"scenes":[...]}.'
    )


def normalize(raw: dict, style: dict, theme_id: str | None) -> dict:
    allowed = set(style["scene_types"])
    scenes = raw.get("scenes", [])
    bad = sorted({s.get("type") for s in scenes if s.get("type") not in allowed}, key=str)
    if bad:
        nomes = ", ".join(map(str, bad))
        raise ContractError(f"Tipos de cena fora do estilo {style['id']}: {nomes}")
    data = {"style": style["id"], "scenes": scenes}
    if theme_id:
        data["theme"] = theme_id
    return contracts.validate("scenes", data)


def prompt(transcript: dict, style: dict, start: float = 0.0,
           end: float | None = None) -> tuple[str, str]:
    """System e user para quem vai gerar o JSON: o agente (padrão) ou um LLMClient (automação)."""
    return build_system(style), compact(transcript, start, end)


def script(transcript: dict, style: dict, llm: LLMClient, theme_id: str | None = None,
           start: float = 0.0, end: float | None = None) -> dict:
    """Caminho de automação: chama o OpenRouter.

    Dentro do Claude Code, prefira prompt() + normalize().
    """
    system, user = prompt(transcript, style, start, end)
    raw = llm.complete_json(system, user)
    return normalize(raw, style, theme_id)
