# feat-03-04-folga-e-fade — Folga de fala e fade nos cortes

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda). Evolui `core/cut.py` (dono de Corte em `concepts.md`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Recorte por `start`/`end` | `core/cut.py` `plan`, `ffmpeg_args` | corte seco, sem folga nem fade | estender | Mesmo dono (Corte) |
| Legenda e zoom no tempo | `core/captions.build_ass`, filtro do zoom (`feat-03-02`) | usam `start` do clip | reusar | Passam a receber o `start` já com a folga |
| Config por tema | `themes/*.json`, `contracts/theme.schema.json` | sem bloco de corte | estender | Campo opcional `cut` para sobrescrever os padrões |
| Referência | `forge-sdd/gravacoes/…14.33.02.reel/zoom_cortes.py` | `ANTES, DEPOIS = 0.40, 0.70`; `FADE_IN, FADE_OUT = 0.25, 0.45` | reusar valores | Funciona nos 5 cortes validados |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, SEG-03, ARQ-05, ARQ-06, ARQ-10, DUP-01, TST-01

## Contexto do defeito
- **Origem:** `feat-01-04-cortar-legenda`.
- **Causa-raiz:** o corte começa e termina exatamente nos limites do segmento, e o áudio e o vídeo entram e saem de forma seca; a fala fica "comida" no começo e no fim.
- **Evidência:** os cortes de `zoom_cortes.py` só ficaram naturais depois de somar folga e aplicar fade.

## Escopo
- **Folga:** `start` passa a `max(0, start - 0.40)` e `end` a `min(duração, end + 0.70)`. A folga vale para tudo que depende do tempo do corte: legenda, zoom no tempo, análise de quadros e `-ss`/`-t`.
- **Fade:** vídeo (`fade`) e áudio (`afade`), entrada de 0.25 s e saída de 0.45 s, com a saída iniciada em `duração - fade_out`. Se o corte for mais curto que `fade_in + fade_out`, os fades são reduzidos proporcionalmente.
- **Padrões e override:** os valores acima são padrão em `core/cut.py`; o tema pode sobrescrever com `cut: {pad_before, pad_after, fade_in, fade_out}` (todos em segundos, `>= 0`). Valores inválidos são rejeitados na borda (`SEG-01`).
- **Limite de duração:** o corte final não passa de 60 s (`discovery 01`); a folga é reduzida (primeiro o depois, depois o antes) se estourar.
- **Dry-run:** mostra o `start`/`end` já ajustados e não escreve (`ARQ-05`).

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_cut.py -k folga`: com `start=10`, `end=30` e duração 100, o corte vai de 9.60 a 30.70; `start=0.2` fica em 0; `end` perto do fim do vídeo fica limitado à duração; estouro de 60 s reduz a folga.
- `uv run pytest tests/test_cut.py -k fade`: o filtro de vídeo contém `fade=t=in:d=0.25` e `fade=t=out:st=<dur-0.45>:d=0.45`, e `-af` contém `afade` equivalentes; corte curto reduz os fades.
- `uv run pytest tests/test_cut.py -k tema_cut`: o tema sobrescreve os padrões; valor negativo é rejeitado.
- `uv run pytest tests/test_cut.py -k folga_zoom`: o `T` relativo do zoom dinâmico usa o `start` com a folga.
- `cd engine && uv run pytest && uv run ruff check` passam.
