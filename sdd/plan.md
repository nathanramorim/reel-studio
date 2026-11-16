# Plano — reel-studio

## Fases

| Fase | Feature | Entrega | Critério resumido |
|------|---------|---------|-------------------|
| 0 | `sdd/discovery/01-reel-studio-mvp` | Esqueleto: plugin, contratos, temas, estilos, motor e render | `uv run pytest` e `npx tsc --noEmit` verdes |
| 1 | `01-reel-studio-mvp` feat 01 a 04 | Modo corte completo (extract, transcribe, suggest, cut) | Gera `clip-01.mp4` com legenda no tema |
| 2 | `01-reel-studio-mvp` feat 05 a 06 | Modo VSL: `script` + render Remotion dos 3 estilos SVG | Gera `vsl.mp4` a partir de `scenes.json` |
| 3 | nova iniciativa | Manim, avatar estilizado (rhubarb), TTS plugável | A definir em discovery |

## Dependências externas
```
typer>=0.12  httpx>=0.27  jsonschema>=4.21
faster-whisper>=1.0 (extra)  demucs>=4.0 (extra)  manim>=0.18 (extra)
remotion 4.x  react 18  ffmpeg (sistema)
```
