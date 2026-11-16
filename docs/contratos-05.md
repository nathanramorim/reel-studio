# Contratos novos da iniciativa 05

- `themes/<id>.json` → `brand` (opcional): `logo` e `mascot` (SVG relativo a `themes/<id>/`, ou `null`), `mono`, `panel` (`radius`, `border`, `bar`, `dots`) e `packet` (`glow`, `radius`). Caminho fora da pasta do tema é rejeitado.
- `clips.json` → `overlays` por corte: `{at, dur, type, text}` com `type` em `hook`, `keyword`, `step`, `callout`, `progress`, `cta`, `logo`; `at` e `dur` em segundos relativos ao corte e dentro dele; `text` até 60 caracteres.
- `scenes.json` → `tone` e `share` (até 280 caracteres) no topo; `media.source {start, end}` por cena.
- `scenes.json` → `normalize` rejeita cena com `dur` abaixo de 0,3 s por palavra exibida mais 0,4 s.
- `render`: `--audio` padrão é `original` quando todas as cenas têm `source`; senão `none`.
- Projetos sem vídeo: `Project.open_text(slug)` cria `reel-projects/<slug>/`.
