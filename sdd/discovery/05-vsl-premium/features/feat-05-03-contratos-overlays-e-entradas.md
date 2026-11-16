# feat-05-03-contratos-overlays-e-entradas — Contratos: `overlays`, entradas conteúdo e livre, `media`

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Cortes | `contracts/clips.schema.json`, `core/suggest.py` | `id`, `start`, `end`, `hook` | estender | Campo `overlays` por corte |
| Cenas | `contracts/scenes.schema.json`, `core/script.py` | `narration`, `source` | estender | Campo `media` por cena; `tone` e `share` no topo |
| Pasta de trabalho | `core/project.py` | exige arquivo de vídeo | estender | Projeto de conteúdo ou ideia, sem vídeo |
| Padrões de voz e legenda | `cli.render_cmd` (`--audio none`) | áudio original opcional | estender | Padrão `original` quando todas as cenas têm `source` |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, ARQ-06, DUP-01, TST-01

## Escopo
- `clips.schema.json`: `overlays` opcional, itens `{at, dur, type, text}` com `type` em `hook`, `keyword`, `step`, `callout`, `progress`, `cta`, `logo`; `at` e `dur` em segundos relativos ao corte, dentro da duração dele; `text` até 60 caracteres.
- `scenes.schema.json`: `media` opcional por cena (`source: {start, end}`), `tone` e `share` (até 280 caracteres).
- `Project.open_text(slug)`: pasta de trabalho para conteúdo ou ideia, em `reel-projects/<slug>/`, sem vídeo.
- `render` passa a usar `--audio original` por padrão quando todas as cenas têm `source` (senão `none`), e `--captions narration` continua o padrão.
- Validação na borda (`SEG-01`); contratos novos documentados.

## Critérios de Aceitação Executáveis
- `cd engine && uv run reel-studio validate` e `uv run pytest tests/test_contracts.py -k "overlays or media or share"`: overlay fora do corte, tipo inválido e texto longo são rejeitados.
- `uv run pytest tests/test_project.py -k open_text`: cria a pasta, sem exigir vídeo, e não toca fora dela.
- `uv run pytest tests/test_render.py -k padrao_voz`: com `source` em todas as cenas o padrão é `original`; sem, `none`.
- `uv run pytest && uv run ruff check` passam.
