# feat-04-03-narracao-no-vsl — Narração no VSL (aguarda decisão)

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; `SceneRenderer` único ponto `type -> componente`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Narration | `scenes.json` (`narration` por cena) | campo sem uso | reusar | Fonte do texto da narração |
| Legenda | `core/captions.py` | `.ass` palavra a palavra | estender | Legenda por cena a partir da `narration` |
| Render | `core/render.py` | só vídeo | estender | Mixa legenda ou áudio no mp4 final |

## Dependências novas
Nenhuma para C; A e B conforme a decisão (B exigiria TTS).

## Rules e IDs da Constituição Aplicáveis
ARQ-05, SEG-03, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** O render do VSL não leva nem a `narration` nem o áudio.
- **Evidência:** `ffprobe`: o `vsl-…mp4` só tem fluxo de vídeo.

## Escopo
**Não despachar antes da decisão do humano.** Recomendado: C como padrão e A opcional.
- **C:** a `narration` de cada cena vira legenda queimada (`.ass` com o tema), dividida em blocos de 3 palavras no tempo da cena; vale para todo VSL.
- **A (`--audio original`):** só se todas as cenas tiverem `source: {start, end}` (campo opcional em `scenes.schema.json`); o áudio de cada trecho é recortado e emendado no ritmo das cenas, com fade curto; sem `source`, erro claro.
- `render --dry-run` mostra o plano e não escreve (`ARQ-05`); ffmpeg por lista de argumentos (`SEG-03`).

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_render.py -k narracao`: a legenda cobre cada cena e respeita `dur`; sem `narration` a cena fica sem legenda.
- `uv run pytest tests/test_render.py -k audio_original`: com `source` nas cenas o plano tem os recortes; sem `source`, erro claro.
- `ffprobe` do mp4 final mostra a legenda queimada (C) ou o fluxo de áudio (A); manual com o clip-05.
