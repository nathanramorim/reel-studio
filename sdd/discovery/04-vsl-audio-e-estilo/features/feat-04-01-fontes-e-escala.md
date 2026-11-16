# feat-04-01-fontes-e-escala — Fontes locais e escala tipográfica para 1080×1920

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; `SceneRenderer` único ponto `type -> componente`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Fontes do tema | `themes/*.json` `fonts.title/body/mono` | só nomes, nunca carregados | estender | Carregar de arquivos locais |
| Tamanhos | `scenes/*.tsx`, `text-fit.ts` | números soltos (20 a 96 px) | estender | Escala única reusada pelas cenas (`DUP-03`) |

## Dependências novas
`@remotion/fonts` e fontes Montserrat (OFL) em `render/public/fonts/`; consultar context7 com a versão exata (`SEG-07`). Sem rede no render.

## Rules e IDs da Constituição Aplicáveis
ARQ-06, DUP-03, SEG-07, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** Nenhum código carrega a fonte do tema, então o Chromium usa serifa; os tamanhos são fixos e pensados para um quadro menor.
- **Evidência:** `vsl-isometric-pastel-forge.mp4`: texto em Times, fonte de 36 px no `flow`, 40 px na lista, blocos pequenos no meio.

## Escopo
- Registro `render/src/fonts.ts`: nome da fonte do tema -> arquivo em `public/fonts/` (Montserrat 500, 700 e 800; JetBrains Mono 500); carregado com `loadFont` antes do primeiro quadro (`delayRender`/`continueRender`).
- Fonte desconhecida cai em `sans-serif` com aviso no console, nunca em serifa.
- `render/src/scale.ts` define a escala para 1080×1920 (título 120 a 72 px por `fitFontSize`, corpo 64, secundário 48, mínimo 44) e todas as cenas a usam, sem números soltos.
- Licença OFL junto das fontes.

## Critérios de Aceitação Executáveis
- `cd render && npx tsc --noEmit` passa.
- `node scripts/check-render.mjs --fonts`: um still de cada cena mostra texto em Montserrat (largura do texto medida difere da serifa de referência) e nenhum `font-family` cai no fallback.
- `node scripts/check-render.mjs --scale`: nenhum texto de cena renderiza abaixo de 44 px.
- Manual: quadros de `title`, `list` e `flow` com fonte do tema e tamanho legível no celular.
