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
`reel-studio script VIDEO --style S` gera `scenes.json` usando só os tipos de cena declarados no `style.json`.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_script.py` (LLM simulado, tipos inválidos rejeitados).
