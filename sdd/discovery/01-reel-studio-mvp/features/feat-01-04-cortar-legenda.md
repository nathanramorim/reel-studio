# feat-01-04-cortar-legenda — Cortar com legenda no tema

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| corte e legenda | engine/ | — | criar | Primeira versão |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05

## Escopo
`reel-studio cut VIDEO --theme T [--dry-run]` recorta cada clip, enquadra em 1080x1920 e queima legenda `.ass` com cores e fonte do tema.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_captions.py`; C6 com vídeo real.
