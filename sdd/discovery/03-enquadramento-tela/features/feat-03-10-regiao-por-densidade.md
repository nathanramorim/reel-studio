# feat-03-10-regiao-por-densidade — Região de zoom por densidade de atividade, na proporção da faixa

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`; análise local; LLM não vê mídia). Evolui `core/frames.py` (`_activity`, `track`) e a escolha em `core/cut.py` (`choose_layout`); `feat-03-01` e `feat-03-02`.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Região de atividade | `frames._activity` | `boundingRect` da união das diferenças; `MAX_REGION_AREA = 0.6` devolve `None` | estender | Troca a caixa por janela de densidade |
| Troca no tempo | `frames.track`, `SHIFT = 0.08`, janelas de 6 s | histerese só pelo centro | estender | Mantém a mecânica; muda o critério e adiciona intervalo mínimo |
| Faixa do conteúdo | `cut.BAND_Y`, `cut.BAND_H` (1080×920) | constantes | reusar | Define a proporção da região |
| Referência manual | `zoom_cortes.py` (`REGIOES`) | regiões 1430×1190 (~1,2) com trocas | reusar como oráculo | Valida o resultado automático |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05, ARQ-10, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-03-01` e `feat-03-02`.
- **Causa-raiz:** o `boundingRect` da união das diferenças se espalha com qualquer mudança isolada (cursor, relógio, Dock, barra de menu) e passa de `MAX_REGION_AREA`, então o corte cai em `fit`. A região também não tem a proporção da faixa, deixando espaço vazio (`clip-01`) ou cortando linhas (`clip-02`).
- **Evidência (C5, gravação 14.33.02):** `clip-03` a `clip-05` caíram em `fit` com o texto ilegível; os cinco cortes têm 0 ou 1 região; no `clip-02` o Dock entrou e as linhas foram cortadas à direita. O manual usa zoom em todos e troca de região no `clip-02` (t=141,35) e no `clip-05` (524 e 536).

## Escopo
- **Região na proporção da faixa:** toda região do `zoom` tem `w/h = 1080/920`, e preenche a faixa sem espaço vazio.
- **Tamanho por cobertura:** testa larguras de 50%, 67% e 80% do quadro e escolhe a menor que cobre pelo menos 85% da atividade da janela. Se nenhuma cobrir, volta para `fit`. Isso substitui `MAX_REGION_AREA`.
- **Posição por densidade:** a janela se centra no centroide da atividade (ponderada por densidade, não por caixa) e é limitada às bordas do quadro.
- **Ruído ignorado:** a barra de menu (topo, ~3%) e o Dock (base, ~8%) não contam como atividade; componentes isolados menores que 0,05% do quadro também não.
- **Troca no tempo:** troca de região quando o centro se afasta `>= SHIFT` ou o tamanho muda de degrau; no mínimo 3 s entre trocas, para não tremer. O `w`×`h` continua fixo no corte, o maior da sequência (`feat-03-02`).
- `fill` por rosto e `fit` para vídeo sem atividade ou sem OpenCV continuam como estão.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_frames.py -k densidade`: com quadros sintéticos, atividade só na metade direita escolhe a janela de 50% à direita; atividade nas duas metades em instantes diferentes gera troca; um ponto isolado longe (relógio) não expande a região; atividade no Dock ou na barra de menu é ignorada; atividade espalhada em mais de 80% da largura devolve `fit`.
- `uv run pytest tests/test_frames.py -k proporcao`: toda região sai com `w/h` igual a 1080/920 (tolerância de 1 px) e dentro do quadro.
- `uv run pytest tests/test_frames.py -k oraculo`: para cada passo de `REGIOES` do `zoom_cortes.py`, a região escolhida cobre pelo menos 80% do retângulo de referência.
- `uv run pytest tests/test_frames.py -k intervalo`: duas trocas nunca ficam a menos de 3 s.
- `cd engine && uv run pytest && uv run ruff check` passam.
- **C5 manual (14.33.02):** `clip-03` a `clip-05` saem em `zoom`; o `clip-02` e o `clip-05` mostram pelo menos uma troca; o Dock não aparece; o texto do terminal fica legível em 1080×1920.
