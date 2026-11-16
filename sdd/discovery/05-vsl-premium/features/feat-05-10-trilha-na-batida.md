# feat-05-10-trilha-na-batida — Trilha e efeitos na grade de batidas

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Trilha do Forge | `forge-sdd/docs/video-pipeline/musica.py` | síntese em Python puro | reusar | Portada para `core/music.py` |
| Mixagem | `core/render.py` (`audio_filter`, `mux_args`) | voz original por cena | estender | Mistura trilha com ducking |
| Durações | `core/render.durations` | duração efetiva da cena | estender | Cortes encaixados na batida |

## Dependências novas
Nenhuma: só biblioteca padrão (`wave`, `struct`, `math`).

## Rules e IDs da Constituição Aplicáveis
ARQ-04, ARQ-05, SEG-03, DUP-03, TST-01

## Escopo
- `core/music.py`: gera o `.wav` determinístico (semente fixa) com andamento vindo do `tone` (padrão 100 a 120 BPM), baixo, harmonia e efeitos suaves nos cortes, tudo na mesma grade de batidas contada do quadro 0.
- `--music auto|on|off` (padrão `auto`): liga quando não há voz (vídeo mudo, conteúdo, livre); desliga quando há voz; com voz ligada, a trilha fica abaixo dela (ducking por `sidechaincompress` ou automação de volume).
- Os limites das cenas se encaixam na batida mais próxima quando a diferença é de até 0,25 s.
- `--dry-run` mostra o plano da trilha sem escrever (`ARQ-05`); `ffmpeg` por lista de argumentos (`SEG-03`).

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_music.py`: duração do `.wav` igual à do vídeo; saída determinística; cortes na grade de batidas.
- `uv run pytest tests/test_render.py -k "musica or ducking"`: `auto` liga sem voz e desliga com voz; com voz o filtro tem ducking.
- `uv run pytest -k batida`: limites de cena se encaixam na batida (±0,25 s) e não encaixam quando passam disso.
- `uv run pytest && uv run ruff check` passam.
