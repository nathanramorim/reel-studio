# Critérios — 05 Reels premium

## Modelo do módulo
`completo` para `render/` (movimento, transições, painéis) e para `core/` (roteiro, batida, trilha, entrega); `enxuto` para os JSON de tema e estilo e para a documentação.

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; o LLM gera `scenes.json`, nunca código de animação; `SceneRenderer` único ponto `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima. ADR-0002 (`doctor`) está na branch da iniciativa 02, ainda não vigente. Constitution: `SEG-01`, `SEG-03`, `SEG-05`, `SEG-07`, `ARQ-04`, `ARQ-05`, `ARQ-06`, `ARQ-10`, `DUP-01`, `DUP-03`, `TST-01`.

## Restrições
- `DUP-01`: um único mapa `type -> componente`; variantes por estilo no registro `styleScenes`.
- `ARQ-06`: campos novos (`brand` do tema, `tone` e `share` do roteiro, `media` da cena) entram nos schemas em `contracts/`.
- `ARQ-04`: trilha e efeitos só com a biblioteca padrão; sem dependência de render nova; transições próprias, sem `@remotion/transitions`.
- `ARQ-05`: `--dry-run` não escreve nada.
- `SEG-03`: ffmpeg e Node por lista de argumentos. `SEG-05`: dados sensíveis nunca em log, vídeo ou copy.
- Sem rede no render; fontes e ativos locais. O modelo de voz é baixado uma vez, na instalação do extra `tts`, nunca durante o render.
- `SEG-05`: amostras de voz e áudio gerado nunca em log, nem fora da pasta do vídeo; a marca d'água do modelo não é removida.
- **Não regredir:** o comando do `ffmpeg` do corte e o `.ass` da legenda ficam idênticos quando não há camadas; o enquadramento automático, o glossário e a folga/fade não mudam.
- Camadas de componentes são compositadas por cima do mp4 do corte (formato com alfa só na composição), nunca no lugar dele (`ARQ-05`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Render por cena | `render/src/scenes/*`, `SceneRenderer.tsx`, `styleScenes.ts` | 8 tipos de cena, registro de variantes | estender | Novo estilo `forge-motion` entra no registro |
| Placas isométricas | `render/src/iso/` | `IsoSlab` em blocos 3D | reusar | Segue como estilo alternativo |
| Fontes e escala | `fonts.ts`, `scale.ts`, `public/fonts` | Montserrat e JetBrains Mono locais; escala 1080×1920 | reusar | Base de tipografia |
| Fundo | `background.tsx` | cor do tema e brilho radial | estender | Grade e brilho animados |
| Movimento | `motion.ts` | `popIn` e `fadeIn` | estender | Spring, escalonamento e easing do Forge |
| Transição entre cenas | `Reel.tsx` | `Sequence` com corte seco | estender | Transições próprias |
| Tema | `themes/*.json`, `theme.schema.json` | cores, gradiente, brilho, fontes, `logo: null` | estender | Bloco `brand` (logo, mascote, painel, pacote) |
| Cores resolvidas | `core/palette.py`, `core/contrast.py` | token vira hex; contraste WCAG | reusar | Sem cor própria no estilo |
| Legenda | `core/captions.py` | `.ass` da narração | estender | Respeita a zona segura |
| Áudio e `source` | `core/render.py` | áudio original por cena; duração efetiva | estender | Mixagem com a trilha |
| Roteiro | `core/script.py` (`prompt`, `normalize`) | cenas, narração, `source` | estender | Gancho, tom, copy |
| Checagem de quadros | `render/scripts/check-render.mjs` | fonte, escala, cobertura, paleta | estender | Zona segura e quadros do meio da transição |
| Layouts de corte | `core/frames.py`, `core/cut.py` | rosto, atividade, região por densidade | reusar sem alterar | Base do corte com componentes e da janela com a tela real |
| Voz e glossário | `core/render.py` (`--audio original`), `core/glossary.py` | voz original com `source`; correções em memória | reusar | Voz é o padrão com vídeo |
| `clips.json` | `contracts/clips.schema.json`, `core/suggest.py` | cortes com `hook` | estender | Campo `overlays` por corte |
| Vídeo do Forge | `forge-sdd/docs/video-pipeline/video.html`, `musica.py` | linguagem de movimento e trilha em Python puro | reusar como referência | Identidade do tema; trilha portada para `core/music.py` |
| `/brag` | `latent-spaces/brag` (MIT) | regras de criação e acabamento | adaptar | Ideias, com créditos |

## Dependências novas
Extra opcional `tts` do uv para a voz gerada (`ARQ-04`): candidato **Chatterbox** (`resemble-ai/chatterbox`, MIT, clona voz de uma amostra, português e ajuste pt-BR, `cpu`/`mps`/`cuda`, marca d'água embutida). Consultar o context7 com a versão exata e confirmar a licença dos pesos (`SEG-07`); registrar a escolha na ADR-0003. O restante não tem dependência nova: o `musica.py` do Forge usa só a biblioteca padrão.

## C4: contexto
```mermaid
graph TB
  User((Criador)) -->|"/gerar-reel (VSL, tom)"| Skill[Skill reel-studio + agente]
  Media[(Vídeo, conteúdo ou ideia)] --> Skill
  Skill -->|cortes + overlays, ou roteiro: gancho, destaques, fecho, copy| CLI[Motor reel-studio]
  CLI --> Render[Render Remotion]
  CLI --> Music[Trilha e efeitos na batida]
  Theme[(Tema: design system + brand)] --> Render
  Out[(mp4 + pôster + share-copy)] 
  Render --> Out
  Music --> Out
```

## C4: contêineres
```mermaid
graph LR
  K[clips.json: overlays] --> L[Camada de componentes: Remotion transparente]
  C0[cut: ffmpeg, intocado] --> F
  L --> F
  S[scenes.json: tone, share, beats, media] --> R[core/render]
  R --> P[props: cores resolvidas, palavras com tempo, brand]
  P --> M[Remotion: forge-motion, transições, painéis]
  R --> A[core/music: grade de batidas + SFX]
  M --> F[ffmpeg: junta vídeo, legenda, trilha, áudio original]
  A --> F
  V[voz de referência: amostra da gravação] --> T[core/voice: clone local]
  T --> R
  T --> W[Whisper local: tempos de palavra]
  W --> P
  F --> O[vsl.mp4 + pôster + share-copy.txt]
  Q[check-render: zona segura + meio da transição] -.-> M
```

## C4: sequência
```mermaid
sequenceDiagram
  participant A as Agente
  participant C as CLI
  participant R as Render
  A->>C: prompt-script (tom)
  C-->>A: roteiro pedido: gancho, destaques, fecho, copy
  A->>C: save-scenes (scenes.json)
  C->>C: normalize (zona segura, leitura, batida)
  C->>R: props (tema, brand, palavras com tempo)
  R-->>C: vídeo com transições
  C->>C: junta trilha, áudio e legenda; pôster no quadro 0
  C-->>A: mp4, pôster e share-copy.txt
```

## Critérios de aceitação executáveis
| # | Critério | Comando |
|---|---|---|
| C1 | Testes e lint do motor | `cd engine && uv run pytest && uv run ruff check` |
| C2 | Typecheck do render | `cd render && npx tsc --noEmit` |
| C3 | Conteúdo lido dentro da zona segura (y 250 a 1536; fora dos 140 px da direita embaixo), com sobreposição das faixas | `cd render && node scripts/check-render.mjs --safe-zone` |
| C4 | Quadros do meio da transição, tirados da linha do tempo, sem dupla exposição e sem sobreposição de texto | `cd render && node scripts/check-render.mjs --transitions` |
| C5 | Tempo de leitura mínimo (0,3 s por palavra) e cortes na grade de batidas | `cd engine && uv run pytest -k "leitura or batida"` |
| C6 | `ffprobe`: pôster no quadro 0, trilha e áudio original, duração igual a frames/fps | `ffprobe` e `ffmpeg` sobre o mp4 |
| C7 | Tema novo ou estilo sem `brand` continua renderizando (compatibilidade) | `uv run pytest -k brand` |
| C8 | **Não regressão:** sem camadas, o comando do `ffmpeg` do corte e o `.ass` são idênticos aos de hoje (teste de igualdade) | `cd engine && uv run pytest -k regressao` |
| C11 | Voz gerada: amostra extraída da gravação, duração das cenas igual à do áudio gerado, tempos de palavra coerentes, consentimento exigido, sem voz sem referência | `cd engine && uv run pytest -k "voz or amostra or consentimento"` |
| C12 | Manual: VSL do clip-05 com a voz gerada a partir da gravação 14.33.02, e conteúdo livre com trilha ligada | `uv run reel-studio render … --voice clone --voice-ref …` |
| C9 | Manual, corte: os 5 cortes da gravação 14.33.02 com componentes por cima, mesmo enquadramento, legenda e voz de hoje | `uv run reel-studio cut … --theme forge` com `overlays` |
| C10 | Manual, VSL: clip-05, tema forge, estilo `forge-motion`, voz original e legenda, comparado com o vídeo do pipeline | `uv run reel-studio render … --style forge-motion --theme forge` |
