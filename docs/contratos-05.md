# Contratos novos da iniciativa 05

- `themes/<id>.json` → `brand` (opcional): `logo` e `mascot` (SVG relativo a `themes/<id>/`, ou `null`), `mono`, `panel` (`radius`, `border`, `bar`, `dots`) e `packet` (`glow`, `radius`). Caminho fora da pasta do tema é rejeitado.
- `clips.json` → `overlays` por corte: `{at, dur, type, text}` com `type` em `hook`, `keyword`, `step`, `callout`, `progress`, `cta`, `logo`; `at` e `dur` em segundos relativos ao corte e dentro dele; `text` até 60 caracteres.
- `clips.json` → `pos` (`top` ou `bottom`, padrão `bottom`) nos overlays `keyword`, `step` e `callout`: faixa abaixo do gancho ou acima da legenda. Ignorado no layout `split`.
- `clips.json` → por corte: `layout` (`fill`, `zoom`, `fit`, `split`; `--layout` da CLI vence), `presenter` (booleano: o mascote do tema, no rodapé à esquerda, reage à fala) e `intro` (`{dur, text}`, `dur` de 0,5 a 3 s, padrão 1,5; `text` padrão é o `hook`). `split`: vídeo em y 250 a 950 e todo o texto abaixo dele. A abertura é um vídeo mudo (composição `Intro`) concatenado antes do corte pronto, gerando `...-abertura.mp4`; sem esses campos nada muda.
- `scenes.json` → `tone` e `share` (até 280 caracteres) no topo; `media.source {start, end}` por cena.
- `scenes.json` → `normalize` rejeita cena com `dur` abaixo de 0,3 s por palavra exibida mais 0,4 s.
- `render`: `--audio` padrão é `original` quando todas as cenas têm `source`; senão `none`.
- Projetos sem vídeo: `Project.open_text(slug)` cria `reel-projects/<slug>/`.
- `styles/forge-motion`: `look.motion` aceita `forge`; o estilo só anima e toda cor vem dos tokens do tema (`brand` opcional: sem ele valem os padrões do painel).
- `cut`: `--overlays auto|none` (padrão `auto`). Com `overlays` no corte, o `ffmpeg` do corte não muda; o Remotion renderiza a composição `Overlay` (ProRes 4444, só durante a composição) e o `ffmpeg` a sobrepõe, gerando `clip-NN-TEMA-overlay.mp4`. `at` é relativo ao corte do `clips.json` (a janela com folga é compensada). `--dry-run` não escreve nada.
