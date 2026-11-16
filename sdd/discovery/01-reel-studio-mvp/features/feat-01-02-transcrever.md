# feat-01-02-transcrever — Transcrever local

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| transcrição | engine/ | — | criar | Primeira versão |

## Dependências novas
`faster-whisper` no extra `transcribe`.

## Rules e IDs da Constituição Aplicáveis
ARQ-04, TST-01

## Escopo
`reel-studio transcribe VIDEO [--model small] [--lang pt]` gera `transcript.json` com palavras e tempos; cache por hash.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_contracts.py` valida um transcript de exemplo no schema.
