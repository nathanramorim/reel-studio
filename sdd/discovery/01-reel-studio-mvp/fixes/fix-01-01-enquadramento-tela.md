# fix-01-01-enquadramento-tela — Corte de gravação de tela some com o conteúdo

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
Nenhuma (ffprobe vem com o ffmpeg).

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05, ARQ-10, TST-01, DUP-03

## Feature Correlacionada
- **Origem:** `sdd/discovery/01-reel-studio-mvp/features/feat-01-04-cortar-legenda.md`.
- **Causa-raiz:** `ffmpeg_args` aplica `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920`. Em vídeo de paisagem, o corte central mantém só uma faixa estreita.
- **Evidência:** `Gravação de Tela 2026-11-15 às 15.04.39.mov` tem 2860×1776. Em 9:16 cabem ~999 px de largura, cerca de 35% da tela; o resto some e o conteúdo fica ilegível.

## Escopo
- `cut --layout auto|fill|fit` (padrão `auto`): vídeo em pé usa `fill`; vídeo em paisagem usa `fit`.
- `fit`: a imagem inteira cabe na largura de 1080, centralizada sobre fundo desfocado do próprio vídeo, e a legenda fica na faixa livre abaixo.
- `focus` com `--region` fica fora e vira feature futura.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_cut.py -k layout`: `auto` escolhe `fit` para 2860×1776 e `fill` para 1080×1920; o filtro de `fit` não contém `crop` do vídeo principal.
- `uv run reel-studio cut "<gravação>" --theme forge --dry-run` mostra o layout escolhido e não escreve nada (`ARQ-05`).
- `cd engine && uv run ruff check` passa.
- Com a gravação real, o mp4 sai 1080×1920 e a tela aparece inteira (conferência manual).
