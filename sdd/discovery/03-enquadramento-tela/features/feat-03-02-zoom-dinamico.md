# feat-03-02-zoom-dinamico — Fundo do tema, faixa do conteúdo e zoom no tempo

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`; LLM não vê mídia). Evolui `feat-03-01`, já entregue no PR #2.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Layouts `fill`/`zoom`/`fit` | `core/cut.py` (`video_filter`, `choose_layout`) | fundo `boxblur`, overlay centralizado, região única por clip | estender | Mesmo dono (Corte) |
| Análise de quadros | `core/frames.py` (`analyze`, `Region`) | uma região por trecho | estender | Passa a devolver regiões por janela de tempo |
| Cor do tema | `themes/*.json` `colors.bg` | existe | reusar | Fundo do pad vem do tema |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05, ARQ-10, DUP-03, TST-01

## Escopo
Validado com `zoom_cortes.py` (gravação 14.33.02) e a edição local do `cut.py` no cache do plugin, que esta feature substitui.
- **Fundo:** pad sólido com `colors.bg` do tema, no lugar do fundo desfocado, em `zoom` e `fit`.
- **Composição:** conteúdo na faixa de altura 920 a partir de y=320, centralizado nela; a legenda `lower-third` fica abaixo, sem sobrepor. Referência: `scale=1080:-2,pad=1080:1920:0:320+(920-ih)/2:color=<bg>`.
- **Zoom dinâmico:** `analyze` divide o trecho em janelas e acha a região de cada uma; `w`×`h` é o maior da sequência e fixo no clip. `x` e `y` do `crop` usam `if(gte(t,T),valor,...)` aninhado, `T` relativo ao início do corte, vírgulas escapadas. Só troca de região se ela se afastar o bastante da anterior (histerese). Troca seca.
- A mudança local no cache do plugin não precisa ser preservada.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_cut.py -k zoom_dinamico`: com os passos do `clip-02` do `zoom_cortes.py` (troca em t=141.35), `x` e `y` saem como `if(gte(t,<T relativo>),…)` com vírgulas escapadas.
- `uv run pytest tests/test_cut.py -k fundo`: o fundo usa `colors.bg` do tema e o filtro não contém `boxblur`.
- `uv run pytest tests/test_cut.py -k faixa`: o conteúdo termina acima da legenda `lower-third`.
- `uv run pytest tests/test_frames.py -k janelas`: região estável não gera troca; deslocamento grande gera.
- `cd engine && uv run pytest && uv run ruff check` passam.
