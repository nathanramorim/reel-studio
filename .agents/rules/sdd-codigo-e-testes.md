---
description: Como manter o motor Python (uv, ruff, pytest) e o render TypeScript limpos, com pendências rastreáveis e critérios executáveis.
globs: ["engine/**", "render/**"]
regras: [COD-01, COD-02, COD-04, COD-06, TST-01, TST-02, TST-05]
---

# Guia Prático — Código Limpo e Testes Executáveis

Rotina para `COD-01`, `COD-02`, `COD-04`, `COD-06`, `TST-01`, `TST-02` e `TST-05` de `sdd/memory/constitution.md` (`GOV-04`).

## 1. Higiene e análise estática (`COD-01`, `COD-02`, `COD-04`, `COD-06`)
- Um módulo de `core/`, uma etapa do pipeline (áudio, transcrição, compactação, corte, legenda, render...).
- Ao substituir comando ou flag, remova o antigo e as referências órfãs na mesma entrega.
- Pendência só como `# TODO(feat-XX): descrição`.
- Após editar: `cd engine && uv run ruff check`. No render, `npx tsc --noEmit`. Nunca `pip`.

## 2. Testes e critérios (`TST-01`, `TST-02`, `TST-05`)
- Cada critério da task vira teste em `engine/tests/test_*.py`, rodado com `cd engine && uv run pytest`, cobrindo caminho feliz e violações.
- Testes nunca baixam modelo nem chamam rede: Whisper, OpenRouter e ffmpeg pesados entram por fixture ou mock (`TST-04`).
- Mudou contrato, tema ou estilo: atualize schema, exemplo e teste no mesmo PR.
