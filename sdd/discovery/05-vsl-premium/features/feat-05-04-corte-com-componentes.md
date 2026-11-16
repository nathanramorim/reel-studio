# feat-05-04-corte-com-componentes — Corte com componentes (camada sobre o corte intacto)

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima. O corte aprovado não pode regredir.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Corte | `core/cut.py` (`plan`, `execute`), `core/frames.py` | enquadramento, legenda, folga e fade | reusar sem alterar | A camada entra depois do corte |
| Render | `core/render.py`, `render/src/Root.tsx` | composição `Reel` | estender | Nova composição `Overlay` transparente |
| Cores e marca | `core/palette.py`, `brand` (`feat-05-02`) | tokens e marca resolvidos | reusar | Componentes sem cor própria |
| Componentes de painel | `feat-05-05` | — | reusar | Moldura de janela compartilhada com o `forge-motion` |

## Dependências novas
Nenhuma nova no motor. Formato com alfa (ProRes 4444) só durante a composição, descartado no fim; confirmar as opções do Remotion no context7 (versão 4.0.543).

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05, ARQ-10, DUP-03, TST-01

## Escopo
- Quando o corte tem `overlays` no `clips.json`: depois do `ffmpeg` gerar o corte, o Remotion renderiza uma camada transparente (`Overlay`: gancho, palavra-chave, passos, moldura de janela, barra de progresso, CTA, logo) com a duração do corte, e o `ffmpeg` a compõe por cima (`overlay`). O arquivo intermediário é apagado.
- Áreas reservadas: topo (gancho e título), moldura ao redor da faixa do conteúdo, faixa acima da legenda (chips e callouts) e rodapé fora da legenda (CTA e logo); tudo dentro da zona segura e sem cobrir a legenda.
- Sem `overlays`, nada muda: o comando do `ffmpeg` e a saída são idênticos aos de hoje.
- `cut --dry-run` mostra o plano (corte e camada) sem escrever; `--overlays none` ignora as camadas.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest -k regressao`: sem `overlays`, o comando do `ffmpeg` e o `.ass` são idênticos; com `overlays`, o comando do corte não muda e há um passo de composição a mais.
- `uv run pytest tests/test_cut.py -k camada`: a camada dura o mesmo que o corte, o intermediário é removido e `--dry-run` não escreve.
- `cd render && node scripts/check-render.mjs --safe-zone`: os componentes do `Overlay` ficam na zona segura e não cobrem a legenda.
- `cd render && npx tsc --noEmit`, `uv run pytest && uv run ruff check` passam.
- Manual (C9): os 5 cortes da gravação 14.33.02 com `overlays`, mesmo enquadramento, legenda e voz de hoje.
