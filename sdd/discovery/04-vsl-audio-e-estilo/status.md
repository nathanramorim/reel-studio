# Status — 04 VSL: áudio e estilo visual

**Status:** 04-01 (fontes e escala) e 04-02 (`isometric-pastel` isométrico) implementadas na branch `feat/04-vsl-audio-e-estilo`; 04-03 (narração) **não** implementada: a spec exige a decisão do humano (A, B ou C) antes do despacho.

**Próximo passo:** revisar o PR de 04-01 e 04-02; decidir a narração (recomendado C com A opcional) e despachar 04-03.

**Verificação:** `npx tsc --noEmit`, `node scripts/check-render.mjs` (fontes, escala e estilo), `uv run pytest`, `uv run ruff check`, `reel-studio validate`. O check precisa de Chrome headless (Remotion baixa na primeira execução).

**A confirmar:** fundo claro próprio do `isometric-pastel` mesmo com tema escuro (aplicado como na spec).
