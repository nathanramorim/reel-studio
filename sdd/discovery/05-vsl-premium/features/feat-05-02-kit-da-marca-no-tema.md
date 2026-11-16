# feat-05-02-kit-da-marca-no-tema — Kit da marca no tema (`brand`)

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Tema | `themes/*.json`, `contracts/theme.schema.json` | cores, fontes, `logo: null` | estender | Bloco opcional `brand` |
| Carga de tema | `core/contracts.load_theme` | valida o JSON | estender | Resolve os ativos dentro da pasta do tema (`SEG-02`) |
| Vídeo e logo do Forge | `forge-sdd/site`, `docs/img` | logo e mascote em SVG, tokens | reusar | Copiados para `themes/forge/brand/` |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, SEG-02, ARQ-06, DUP-01, TST-01

## Escopo
- `theme.schema.json` aceita `brand`: `logo` e `mascot` (caminho de SVG ou `null`), `mono` (fonte), `panel` (`radius`, `border`, `bar`, `dots`) e `packet` (`glow`, `radius`). Tudo opcional.
- `load_theme` resolve os caminhos relativos à pasta do tema e rejeita saída dela.
- `themes/forge.json` ganha `brand` com o logo e o mascote do Forge e as regras de painel e pacote do vídeo do pipeline (barra com 3 pontos, cantos de 18 px, glow).
- Tema sem `brand` continua renderizando como hoje.

## Critérios de Aceitação Executáveis
- `cd engine && uv run reel-studio validate`: `forge` com `brand` válido; caminho fora da pasta do tema é rejeitado.
- `uv run pytest -k brand`: carga resolve os ativos; tema sem `brand` carrega igual (compatibilidade).
- `cd render && npx tsc --noEmit`, `uv run pytest && uv run ruff check` passam.
