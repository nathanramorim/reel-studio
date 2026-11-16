# feat-05-05-estilo-forge-motion — Estilo `forge-motion`: painéis, pacotes, degradê, fundo e câmera vivos

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Estilos e registro | `styles/*/style.json`, `render/src/styleScenes.ts` | `isometric-pastel` por registro | estender | Entrada nova `forge-motion` |
| Movimento | `render/src/motion.ts` | `popIn`, `fadeIn` | estender | Easing cúbico e molas do Forge, escalonamento |
| Fundo | `render/src/background.tsx` | cor e brilho | estender | Grade deslizando e brilho que respira |
| Fontes e escala | `fonts.ts`, `scale.ts` | Montserrat, JetBrains Mono | reusar | Mono para termos técnicos |
| Marca | `brand` (`feat-05-02`) | painel, pacote, logo | reusar | Componentes leem o `brand` |
| Referência | `forge-sdd/docs/video-pipeline/video.html` | painéis, pacotes, cartões, degradê | reusar como referência | Linguagem do Forge |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-06, DUP-01, DUP-03, TST-01

## Escopo
- `styles/forge-motion/style.json`: `renderer: remotion`, `background: theme`, paleta por tokens do tema, `motion: forge`.
- Componentes em `render/src/forge/`: `Pane` (janela com barra e 3 pontos), `Packet` (pílula com glow que percorre um caminho), `Card` (borda superior colorida), `Chip`, `GradText` (degradê do tema), `LiveBackground` (grade e brilho animados) e `Camera` (avanço suave por cena).
- Cenas: `flow` vira painéis ligados com pacotes que andam; `title`/`highlight` em `GradText` sobre `Card`; `list` em `Card` com escalonamento; `compare` em dois `Pane`; `cta` com o comando em mono.
- Registro em `styleScenes.ts`; o `SceneRenderer` continua único mapa `type -> componente`. Respeita a zona segura (`feat-05-01`).

## Critérios de Aceitação Executáveis
- `cd engine && uv run reel-studio validate`: `forge-motion` valida no schema.
- `cd render && node scripts/check-render.mjs --style forge-motion`: um still por tipo de cena com fonte sem fallback, menor texto >= 44 px, conteúdo na zona segura, fundo do tema `forge` e cores só dos tokens.
- `cd render && npx tsc --noEmit`, `uv run pytest && uv run ruff check` passam.
- Manual (C10): VSL do clip-05, tema forge, estilo `forge-motion`, comparado com o vídeo do pipeline.
