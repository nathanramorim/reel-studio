# Fluxos — reel-studio

## Modo corte (vídeo bom, dentro do Claude Code)
```mermaid
sequenceDiagram
  participant U as Usuário
  participant A as Agente (Claude)
  participant C as CLI
  A->>C: extract + transcribe video.mp4
  C-->>A: transcript.json (cache por hash)
  A->>C: prompt-suggest --max 5
  C-->>A: system + transcrição compactada
  A->>A: gera cortes.json
  A->>C: save-clips --file cortes.json
  C-->>U: clips.json para aprovar ou editar
  U->>A: aprova
  A->>C: cut --theme acme
  C-->>U: output/clip-01.mp4 ...
```

## Modo VSL (vídeo ou áudio ruim, dentro do Claude Code)
```mermaid
sequenceDiagram
  participant U as Usuário
  participant A as Agente (Claude)
  participant C as CLI
  participant R as Remotion
  A->>C: prompt-script --style isometric-pastel
  C-->>A: system + transcrição compactada + tipos de cena do estilo
  A->>A: gera roteiro.json
  A->>C: save-scenes --file roteiro.json --theme acme
  C-->>U: scenes.json para aprovar ou editar
  U->>A: aprova
  A->>C: render --theme acme
  C->>R: scenes.json + tema + estilo
  R-->>U: output/vsl.mp4
```

## Caminho de automação (sem agente: CI, cron)
`suggest`/`script` substituem `prompt-*`/`save-*` e chamam o OpenRouter direto, com `OPENROUTER_API_KEY`.
