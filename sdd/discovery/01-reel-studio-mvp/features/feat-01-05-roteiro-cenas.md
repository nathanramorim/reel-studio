# feat-01-05-roteiro-cenas — Roteiro em cenas

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| roteiro | engine/ | — | criar | Primeira versão |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-04, DUP-04

## Escopo
`reel-studio prompt-script VIDEO --style S` mostra o prompt para o agente gerar o JSON; `reel-studio save-scenes VIDEO --style S --file X.json` valida (só os tipos de cena do `style.json`) e grava `scenes.json`. `reel-studio script` faz o mesmo via OpenRouter (caminho de automação).

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_script.py` (LLM simulado, tipos inválidos rejeitados).
