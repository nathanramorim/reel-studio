---
description: Como cumprir as fronteiras do reel-studio (CLI na borda, domínio em core/, render por componentes), recursos estáticos, --dry-run e o modelo de módulo.
globs: ["engine/**", "render/**", "contracts/**", "themes/**", "styles/**", "skills/**", "sdd/spec/**"]
regras: [ARQ-01, ARQ-02, ARQ-03, ARQ-04, ARQ-05, ARQ-06, ARQ-11]
---

# Guia Prático — Arquitetura e Fronteiras de Módulos

Como aplicar `ARQ-01` a `ARQ-06` e `ARQ-11` de `sdd/memory/constitution.md` (`GOV-04`).

## 1. Borda e domínio (`ARQ-01`, `ARQ-02`, `ARQ-06`)
- `engine/src/reel_studio/cli.py` (typer) é a borda: argumentos, validação, chamada ao `core/` e saída. Faz o papel de `cmd/`.
- `engine/src/reel_studio/core/` é o domínio (papel de `internal/`): nunca importa `cli.py`; módulos sem ciclo.
- Comando novo documenta as flags no `--help`, em `commands/` e na skill (`skills/reel-studio/`).
- Contratos entre etapas são JSON Schemas em `contracts/`; mudou o contrato, atualize schema, `core/contracts.py` e testes no mesmo PR.

## 2. Recursos, dependências e `--dry-run` (`ARQ-03`, `ARQ-04`, `ARQ-05`)
- Marca é dado em `themes/*.json`; linguagem visual é `styles/<estilo>/`; cenas são componentes prontos em `render/src/`. O LLM nunca gera código de animação.
- Dependências pesadas entram como extra opcional do `engine/pyproject.toml` (`transcribe`, `voice`, `vision`), nunca no núcleo. Sempre `uv add`; nunca `pip`.
- Simulação (`--dry-run`) não grava em disco.

## 3. Modelo na spec (`ARQ-11`)
- Toda `feat-XX-*.md` declara `## Modelo do módulo`: `enxuto` (docs, prompts, ajustes pontuais) ou `completo` (novo estado, contrato ou etapa do pipeline).
