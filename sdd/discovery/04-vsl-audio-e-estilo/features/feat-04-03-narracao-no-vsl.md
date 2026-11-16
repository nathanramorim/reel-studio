# feat-04-03-narracao-no-vsl — Narração no VSL: legenda (C) e áudio original (A), por opção

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
Nenhuma (ffmpeg e `core/captions.py` já existem). TTS (B) segue na fase 3.

## Rules e IDs da Constituição Aplicáveis
SEG-01, SEG-03, ARQ-05, ARQ-06, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** O render do VSL não leva nem a `narration` nem o áudio.
- **Evidência:** `ffprobe`: o `vsl-…mp4` só tem fluxo de vídeo.

## Escopo
Decisão do humano: **A e C, cada um por opção**, combináveis.
- **C, `--captions narration|none` (padrão `narration`):** a `narration` de cada cena vira legenda queimada (`.ass` com o tema, via `core/captions.py`), em blocos de 3 palavras distribuídos no tempo da cena. Cena sem `narration` fica sem legenda.
- **A, `--audio original|none` (padrão `none`):** o áudio de cada trecho de origem é recortado do vídeo e emendado, com fade curto de 0,05 s nas emendas. Exige `source: {start, end}` em todas as cenas (campo opcional em `scenes.schema.json`, dentro da duração do vídeo); sem `source`, erro claro com a lista de cenas sem ele.
- **Duração com A:** a duração efetiva da cena é o maior entre `dur` e o comprimento do trecho, para não cortar a fala; o render usa essa duração. A sincronia entre legenda e áudio segue a mesma duração.
- **`source` pelo agente:** `prompt-script` passa a pedir `source` por cena (opcional) e `normalize` o valida contra a transcrição (início < fim, dentro do vídeo, sem sobrepor outra cena).
- **Combinações:** A e C juntos (voz real mais legenda), só A, só C, ou nenhum dos dois.
- `render --dry-run` mostra o plano e não escreve (`ARQ-05`); ffmpeg por lista de argumentos (`SEG-03`); entradas validadas na borda (`SEG-01`).

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_render.py -k captions`: C cobre cada cena e respeita a duração; `--captions none` não gera legenda; cena sem `narration` fica sem legenda.
- `uv run pytest tests/test_render.py -k audio_original`: com `source` em todas as cenas o plano tem os recortes e as emendas com fade; sem `source`, erro lista as cenas; `--audio none` não gera fluxo de áudio.
- `uv run pytest tests/test_render.py -k duracao`: com A, a duração da cena é o maior entre `dur` e o trecho.
- `uv run pytest tests/test_script.py -k source`: `prompt-script` pede `source`; `normalize` rejeita trecho fora do vídeo, invertido ou sobreposto.
- `cd engine && uv run pytest && uv run ruff check` passam.
- Manual (clip-05): `render` com `--audio original --captions narration` traz fala e legenda; só `--captions narration` traz só legenda; `ffprobe` confere o fluxo de áudio.
