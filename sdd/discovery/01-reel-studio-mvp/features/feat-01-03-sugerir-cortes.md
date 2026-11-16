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
`reel-studio prompt-suggest VIDEO --max 5` mostra o prompt (system + transcrição compactada) para o agente gerar o JSON; `reel-studio save-clips VIDEO --file X.json` valida e grava `clips.json` com cortes alinhados a segmentos. `reel-studio suggest` faz o mesmo chamando o OpenRouter (caminho de automação, sem agente).

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_compact.py tests/test_suggest.py` (LLM simulado).
