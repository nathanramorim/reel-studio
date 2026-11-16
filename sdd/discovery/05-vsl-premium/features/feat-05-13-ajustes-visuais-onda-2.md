# feat-05-13-ajustes-visuais-onda-2 — Ajustes visuais do corte com componentes e do `forge-motion`

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; CLI na borda, domínio em `core/`). Iniciativa 05: o corte aprovado (enquadramento, legenda, voz, folga e fade) não pode regredir.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Gancho do corte | `core/captions.build_ass` (`hook`), `clips.json` `hook` | desenha o `hook` do corte no `.ass` | estender | Não desenhar quando houver overlay `hook` |
| Overlay `hook` | `render/src/overlay/Overlay.tsx` | gancho em chip | reusar | Passa a ser o único gancho quando existir |
| Cenas do `forge-motion` | `render/src/forge/ForgeScenes.tsx`, `Pane.tsx`, `Card.tsx` | blocos pequenos, ocupam ~490 a 1290 px dos 1920 | estender | Mais escala e centralização acima da legenda |
| CTA | `render/src/forge/` (cena `cta`), `Overlay.tsx` (`cta`) | quebra deixa uma palavra sozinha | estender | Quebra equilibrada |
| Checagem de quadros | `render/scripts/check-render.mjs` | zona segura, fonte, escala, faixa vazia (<= 25%) | estender | Preenchimento e folga até a legenda |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-05, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-05-04` e `feat-05-05`, vistos no C9 e C10 manuais (gravação 14.33.02, tema forge).
- **Evidência:** `clip-02-forge-overlay.mp4` mostra dois ganchos empilhados no topo; `vsl-forge-motion-forge.mp4` deixa o bloco em 490 a 1290 px, com a legenda encostada no último painel do `flow`, e o CTA quebra "ok" sozinho.

## Escopo
1. **Gancho duplicado:** quando o corte tem um overlay `hook`, o `hook` do `clips.json` não é desenhado no `.ass`. Sem overlay `hook`, nada muda (o `.ass` e o comando do `ffmpeg` seguem idênticos).
2. **Preenchimento do `forge-motion`:** painéis, cartões e texto maiores, com o conteúdo centralizado na zona útil (y 250 a 1536), sempre com folga mínima de 40 px até a legenda.
3. **CTA:** quebra equilibrada, sem palavra sozinha na última linha, no `Overlay` e na cena `cta` do `forge-motion`.
4. **Chips sobre a gravação (decisão pendente do humano):** `keyword` e `step` caem sobre a parte de baixo da gravação, e o logo cobre um canto do editor. Opções: manter como chamado (callout) sobre o conteúdo; mover para o topo, junto do gancho; ou reduzir a faixa do vídeo quando houver chips, o que mudaria o enquadramento (não recomendado). Implementar só depois da escolha.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest -k regressao`: sem overlay `hook`, o `.ass` e o comando do `ffmpeg` são idênticos; com overlay `hook`, o `.ass` não traz o `hook` do corte.
- `uv run pytest tests/test_captions.py -k hook_duplicado`: cobre os dois casos.
- `cd render && node scripts/check-render.mjs --style forge-motion --fill`: faixa vazia vertical <= 15% da zona útil e folga >= 40 px entre o conteúdo e a legenda, em todos os tipos de cena.
- `cd render && node scripts/check-render.mjs --cta`: nenhuma linha do CTA fica com uma palavra só, no `Overlay` e no `forge-motion`.
- `cd render && npx tsc --noEmit` e `cd engine && uv run pytest && uv run ruff check` passam.
- Manual: refazer `clip-02-forge-overlay.mp4` e `vsl-forge-motion-forge.mp4` e comparar.
