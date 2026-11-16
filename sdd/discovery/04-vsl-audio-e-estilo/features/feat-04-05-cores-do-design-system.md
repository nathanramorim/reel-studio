# feat-04-05-cores-do-design-system — Estilo só anima; as cores vêm do design system do projeto

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes: estilo = linguagem visual e movimento; tema = marca). `core/` resolve as cores; o render só lê hex (`DUP-01`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Tokens de cor | `themes/*.json`, `contracts/theme.schema.json` | `bg`, `surface`, `text`, `muted`, `accent`, `accent2`, `success` | estender | Campos opcionais `glow` e `gradient` |
| Design system do Forge | `forge-sdd/site/src/styles/global.css`, `docs/img/banner.svg` | `bg #0d0f14`, brilho `#1e2a4a`, acento `#4f8ef7`, degradê `#4f8ef7 → #8aa4ff → #3ecf8e`, `ok`, `warn`, `bad` | reusar como fonte do `forge.json` | Sem inventar cores |
| Cores dos estilos | `styles/*/style.json` (`look.bg`, `look.palette` em hex; `background: own` em 3 dos 4) | cores próprias de cada estilo | estender | Passam a nomes de token do tema |
| Fundo | `render/src/background.tsx` | cor sólida | estender | Aceita o brilho radial do tema |
| Props do render | `core/render.props`, `feat-04-04` | resolve contraste | estender | Resolve também a paleta |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, ARQ-06, DUP-01, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** os estilos trazem cores próprias (fundo claro, preto, degradê azul e roxo) que ignoram o design system do projeto que está sendo gerado.
- **Evidência:** `vsl-isometric-pastel-forge.mp4` e `vsl-whiteboard-explainer-forge.mp4`; o degradê azul e roxo do `flat-vector-science` não existe no design system do Forge.

## Escopo
- **Decisão do humano:** o estilo entrega a animação e a forma; **toda cor vem do tema**.
- **Tema:** `contracts/theme.schema.json` aceita `colors.glow` (cor do brilho radial de fundo) e `colors.gradient` (2 a 4 cores); `colors.warn` e `colors.bad` opcionais. `themes/forge.json` e `pessoal.json` ganham `glow #1e2a4a`, `gradient [#4f8ef7, #8aa4ff, #3ecf8e]` e os tokens `warn`/`bad` do design system.
- **Fundo:** `background.tsx` desenha o `bg` do tema com um brilho radial (`glow`) a 50% x 25%, como no banner do Forge; sem `glow`, só o `bg`.
- **Estilos:** os quatro passam a `background: theme`. `look.palette` troca hex por nomes de token (`["accent", "accent2", "success", "warn"]`), que `core/render.props` resolve para as cores do tema (`core/palette.py`), com variações de tom de topo e laterais para as placas isométricas. Sem o token no tema, usa tons derivados do `accent`. `look.bg` sai dos estilos entregues; `background: own` continua válido no contrato como opt-in, mas nenhum estilo entregue o usa.
- **Contraste:** a `feat-04-04` continua como rede de segurança.

## Critérios de Aceitação Executáveis
- `cd engine && uv run reel-studio validate` aceita `glow`, `gradient` e tokens de paleta; rejeita `gradient` com menos de 2 cores.
- `uv run pytest tests/test_palette.py`: tokens viram os hex do tema (`forge` -> `#4f8ef7`, `#8aa4ff`, `#3ecf8e`); token ausente cai em tons do `accent`; tons de topo e laterais mais claro e mais escuro que a base.
- `uv run pytest tests/test_render.py -k cores`: nenhum estilo entregue tem hex próprio nem `background: own`; props do `forge` x cada estilo trazem o fundo e a paleta do `forge`.
- `cd render && npx tsc --noEmit` passa.
- `cd engine && uv run pytest && uv run ruff check` passam.
- Manual (clip-05, tema forge): `isometric-pastel` e `whiteboard-explainer` com o fundo e as cores do Forge.
