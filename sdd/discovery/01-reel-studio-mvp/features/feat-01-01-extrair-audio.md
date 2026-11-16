# feat-01-01-extrair-audio — Extrair áudio e isolar voz

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| extração de áudio | engine/ | — | criar | Primeira versão |

## Dependências novas
Nenhuma na base; `demucs` no extra `voice`.

## Rules e IDs da Constituição Aplicáveis
ARQ-01, SEG-03

## Escopo
`reel-studio extract VIDEO [--voice-only]` gera `audio.wav` (16 kHz mono) e, com `--voice-only`, `voice.wav`.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_audio.py` confere os argumentos do ffmpeg (lista, sem shell).
