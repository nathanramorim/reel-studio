# ADR-0004: Python sempre via uv

- **Data:** 2026-11-19
- **Status:** `aprovado` (retrodocumentado: já em vigor desde o scaffold)
- **Regras afetadas (IDs da constitution):** `ARQ-04`, `COD-02`, Regra 6
- **Autor / Responsável:** dono do repositório

## Contexto

O motor roda na máquina de quem instala o plugin. Instruções com pip e venv manual quebram e poluem o ambiente. O projeto já usa `engine/pyproject.toml` + `engine/uv.lock` e o README manda `uv sync` e `uv run reel-studio ...`.

## Opções Consideradas

1. **pip + requirements.txt:** frágil, global, sem lock.
2. **uv com `pyproject.toml`, `uv.lock` e extras opcionais:** reprodutível, um comando.

## Decisão

Opção 2. Dependências pesadas como extras (`transcribe`, `voice`, `vision`), instaladas com `uv sync --extra <nome>`; testes e lint no grupo `dev` (`uv run pytest`, `uv run ruff check`). Nunca escrever `pip` em código, docs ou skill.

## Consequências

- **Positivas:** instalação reprodutível; o README e a skill usam o mesmo comando.
- **Negativas / Trade-offs:** exige `uv` instalado.
- **Ações de acompanhamento:** README lista `uv` em `## Requisitos` (verificador do readme-studio barra `pip install`).
