# feat-05-07-transicoes-entre-cenas — Transições entre cenas

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Montagem das cenas | `render/src/Reel.tsx` | `Sequence` com corte seco | estender | Camada de transição própria |
| Movimento | `render/src/motion.ts` | easing básico | reusar | Curvas do Forge |
| Linha do tempo | — | — | criar | `render/src/timeline.ts` exporta os limites de cada cena para as checagens |

## Dependências novas
Nenhuma; sem `@remotion/transitions` (`ARQ-04`).

## Rules e IDs da Constituição Aplicáveis
DUP-03, TST-01

## Escopo
- Cada cena pode ter `transition`: `cut`, `dip` (passa pelo fundo), `wipe` ou `slide`; o padrão vem do `tone` (`feat-05-09`) e, sem tom, é `dip`.
- Sai o conteúdo antigo e entra o novo, de forma escalonada: a soma das opacidades nunca passa de 1,05 e nenhum texto de cenas diferentes se sobrepõe. Duração de 0,35 s dentro do tempo das cenas.
- `timeline.ts` expõe início e fim de saída e de entrada por cena para a checagem de quadros do meio da transição.

## Critérios de Aceitação Executáveis
- `cd render && node scripts/check-render.mjs --transitions`: stills tirados da linha do tempo (fim da saída e início da entrada) sem dupla exposição e sem sobreposição de texto.
- `cd render && npx tsc --noEmit` passa; `uv run pytest -k transicao` valida o campo `transition` no schema.
- `cd engine && uv run pytest && uv run ruff check` passam.
