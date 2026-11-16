# Overview — reel-studio

Plugin do Claude Code com motor local que transforma vídeos gravados em reels 9:16. Dois modos: **corte** (recorta o vídeo real, com legenda na marca) e **VSL** (reescreve como roteiro curto e anima em um dos estilos). O LLM só lê a transcrição.

## Índice
- `stack.md` — tecnologias
- `modules.md` — componentes
- `flows.md` — fluxos principais
- `decisions.md` — decisões de design
- `concepts.md` — dono de cada conceito
- `adr/adr-0001-arquitetura-base.md` — decisões base

---

## Arquitetura (C4 Model)

### Nível 1: Contexto
```mermaid
graph TB
  User((Criador)) -->|"/gerar-reel"| Claude[Claude Code + skill reel-studio]
  Claude -->|CLI| Engine[reel-studio engine]
  Engine -->|texto compactado| LLM[OpenRouter]
  Engine --> Out[(reels .mp4)]
```

### Nível 2: Containers
```mermaid
graph LR
  Skill[skills/reel-studio] --> CLI[engine: CLI uv]
  CLI --> FF[ffmpeg]
  CLI --> W[faster-whisper]
  CLI --> LLM[OpenRouter]
  CLI --> R[render: Remotion]
  CLI --> M[render: Manim]
  R --> T[(themes + styles)]
  M --> T
```
