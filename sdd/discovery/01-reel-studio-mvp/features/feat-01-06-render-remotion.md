# feat-01-06-render-remotion — Render Remotion

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| render | engine/ | — | criar | Primeira versão |

## Dependências novas
`remotion`, `@remotion/cli`, `react`.

## Rules e IDs da Constituição Aplicáveis
ARQ-05, ARQ-06

## Escopo
`reel-studio render VIDEO --theme T [--dry-run]` chama o Remotion com `scenes.json` + tema + estilo. Tipos de cena: title, highlight, flow, list, compare, cta (fase 2 completa os 3 estilos).

## Critérios de Aceitação Executáveis
- `cd render && npx tsc --noEmit`.
