# feat-01-03-sugerir-cortes — Sugerir cortes

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| escolha de trechos | engine/ | — | criar | Primeira versão |

## Dependências novas
`httpx`.

## Rules e IDs da Constituição Aplicáveis
SEG-04, SEG-05, DUP-01

## Escopo
`reel-studio suggest VIDEO --max 5` compacta a transcrição, faz uma chamada e grava `clips.json` com cortes alinhados a segmentos.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_compact.py tests/test_suggest.py` (LLM simulado).
