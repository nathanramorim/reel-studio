# feat-03-01-layout-automatico — Layout automático do corte (pessoa e tela)

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (`core/` é o domínio; CLI é a borda). Módulo dono: `core/cut.py` (`concepts.md`, Corte).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Enquadramento 9:16 | `core/cut.py` `ffmpeg_args` | `scale…increase` + `crop`, só preenche | estender | Escolher o layout por vídeo no mesmo módulo |
| Dimensões do vídeo | `core/` | nenhuma | criar | Sonda via ffprobe em `core/proc.py`, sem módulo novo |

## Dependências novas
`opencv-python-headless`, extra opcional `vision` do uv (`ARQ-04`): detecção de rosto e de região com atividade, tudo local. Consultar context7 com a versão exata na implementação (`SEG-07`). Sem o extra, o corte cai em `fit`.

## Rules e IDs da Constituição Aplicáveis
SEG-03, SEG-07, ARQ-04, ARQ-05, ARQ-10, TST-01, DUP-03

## Contexto do defeito
- **Origem:** `sdd/discovery/01-reel-studio-mvp/features/feat-01-04-cortar-legenda.md`.
- **Causa-raiz:** `ffmpeg_args` aplica `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920`. Em vídeo de paisagem, o corte central mantém só uma faixa estreita.
- **Evidência:** `Gravação de Tela 2026-11-15 às 15.04.39.mov` tem 2860×1776. Em 9:16 cabem ~999 px de largura, cerca de 35% da tela; o resto some e o conteúdo fica ilegível.

## Escopo
Tudo automático; a pessoa não passa parâmetro. Três layouts, escolhidos por vídeo:
- **`fill`:** vídeo em pé, ou paisagem com rosto consistente (corte centrado no rosto, rosto com pelo menos ~8% da altura do quadro).
- **`zoom`:** paisagem sem rosto (gravação de tela). Amostra quadros do trecho, compara um com o outro, acha a região com atividade (digitação, saída, cursor), recorta com margem e amplia para a largura de 1080. O resto do quadro vira fundo desfocado; a legenda fica na faixa livre.
- **`fit`:** tela inteira na largura de 1080 sobre fundo desfocado. É o fallback quando a atividade está espalhada pela tela, quando não há movimento e quando falta o OpenCV.
- O `cut` imprime o layout escolhido (ex.: `layout: zoom (2860x1776)`).
- `--layout` e `--anchor` existem só como override raro; a skill não pergunta nada.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_cut.py -k layout`: sem parâmetro, escolhe `fit` para 2860×1776 sem rosto, `fill` centrado no rosto para paisagem com rosto e `fill` para 1080×1920; paisagem sem rosto e com atividade concentrada usa `zoom`; atividade espalhada, parada ou sem OpenCV usa `fit`; o filtro de `fit` não contém `crop` do vídeo principal.
- `pytest -k anchor`: `--anchor left` e `right` mudam o `x` do `crop`; valor fora de 0 a 1 é rejeitado na borda (`SEG-01`).
- `uv run reel-studio cut "<gravação>" --theme forge --dry-run` mostra o layout escolhido e não escreve nada (`ARQ-05`).
- `cd engine && uv run ruff check` passa.
- Com a gravação real, o mp4 sai 1080×1920 e o texto da região ativa fica legível (conferência manual).
