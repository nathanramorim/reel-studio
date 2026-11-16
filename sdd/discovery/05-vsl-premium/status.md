# Status — 05 Reels premium

**Status:** Ondas 1 e 2 mescladas (PRs #4 e #6). Ondas 3 e 4 (05-06 a 05-12) no PR #5: SEG-07 resolvido (pesos e pacote MIT, ADR-0003 e `uv.lock` verificados, extras importam). 05-13 feita (item 4: campo `pos` `top`/`bottom` nos chips, padrão `bottom`) (gancho único, `forge-motion` preenchido acima da legenda, CTA balanceado); `check-render --all`, pytest (248) e ruff passam.

**C9 e C10 refeitos (2026-11-16):** corte com gancho único, logo e barra; VSL `forge-motion` com conteúdo acima da legenda (`/tmp/reel-c10/.../vsl-forge-motion-forge.mp4`). `check-render --all` passa.

**Próximo passo:** você valida C12 (voz pt-BR, exige `--confirm-own-voice`) e dá o aceite visual do C9/C10; então mesclar o PR #5 e promover a ADR-0003 a `aprovado`.

**A confirmar:** usar `pos: "top"` nos cortes em que o rodapé da gravação importa; refazer `clip-02-forge-overlay.mp4` e `vsl-forge-motion-forge.mp4` para comparar.
