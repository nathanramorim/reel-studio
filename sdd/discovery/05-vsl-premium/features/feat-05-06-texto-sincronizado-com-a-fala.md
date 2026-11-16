# feat-05-06-texto-sincronizado-com-a-fala — Texto sincronizado com a fala

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Tempos de palavra | `transcript.json`, `core/captions.words_in` | palavras com início e fim | reusar | Fonte dos tempos |
| Props do render | `core/render.props` | cenas, tema, estilo | estender | Entrega `words` por cena |
| Texto das cenas | `render/src/forge/GradText` (`feat-05-05`) | — | estender | Revela palavra a palavra |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-10, DUP-03, TST-01

## Escopo
- `core/render.props` entrega `words` por cena: com áudio original, as palavras dentro do `source` da cena, remapeadas para o tempo da cena; com voz gerada, as palavras alinhadas do áudio gerado (`feat-05-11`); sem tempos, distribuição uniforme pelo tempo da cena (fallback).
- `GradText` e as cenas do `forge-motion` revelam as palavras no tempo da fala; termos entre crases no `text` saem em mono; as palavras-chave, em degradê.
- Cada quadro é função do tempo (sem estado entre quadros).

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_render.py -k palavras`: remapeamento pelo `source`; fallback uniforme; nenhuma palavra antes do início da cena.
- `cd render && node scripts/check-render.mjs --style forge-motion --words`: nenhuma palavra visível antes do seu tempo e todas visíveis ao fim.
- `cd render && npx tsc --noEmit`, `uv run pytest && uv run ruff check` passam.
