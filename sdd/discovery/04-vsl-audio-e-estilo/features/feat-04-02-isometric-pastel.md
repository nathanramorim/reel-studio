# feat-04-02-isometric-pastel — `isometric-pastel` isométrico, pastel e com o quadro bem usado

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; `SceneRenderer` único ponto `type -> componente`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Estilo | `styles/isometric-pastel/style.json` | `background: theme`, paleta usada só em borda | estender | Passa a `own`, com `look.ink` e paleta como cores de preenchimento |
| Cenas | `render/src/scenes/*` | componentes planos, iguais em todos os estilos | estender | Variante isométrica por estilo, num registro |
| Contrato do estilo | `contracts/style.schema.json` | sem cor de texto | estender | Campo `look.ink` (`ARQ-06`) |
| Fundo e fontes | `background.tsx`, `feat-04-01` | `own` usa `look.bg` | reusar | Sem código novo de fundo |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-06, DUP-01, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** O estilo só troca cores e borda; não há projeção isométrica, a paleta pastel quase não aparece, o fundo vem do tema (preto no `forge`) e o conteúdo fica no centro com muito espaço vazio.
- **Evidência:** Quadro do `flow` no clip-05: quatro caixas escuras empilhadas no meio de 1080×1920, setas verticais, fundo `#0d0f14`.

## Escopo
- `isometric-pastel` usa `background: own` (`#f6f1ea`), com `look.ink` (texto escuro) no contrato e no JSON; o tema entrega acento (no lugar do coral), fontes e CTA. Tema claro ou escuro não muda o fundo do estilo.
- Componente único `IsoSlab` (projeção de 30°, três tons por face: topo, lateral esquerda, lateral direita, sombra longa) preenchido com a paleta em ciclo e o acento do tema.
- Variante do estilo por registro (`styleScenes`): o `SceneRenderer` continua único mapa `type -> componente` e escolhe a variante pelo `style.id`; estilos sem variante usam os componentes atuais.
- **`flow`:** os passos viram placas em escada diagonal pelo quadro (ocupa pelo menos 70% da altura útil), ligadas por setas ao longo dos eixos isométricos; número, rótulo grande e entrada em sequência.
- **`title`, `highlight`, `cta`:** a frase sobre uma placa grande flutuante, ocupando a largura útil; **`list`:** itens em placas empilhadas; **`compare`:** duas placas lado a lado.
- Margens de segurança de 80 px e conteúdo distribuído na altura, sem faixa vazia maior que 25% do quadro.

## Critérios de Aceitação Executáveis
- `cd engine && uv run reel-studio validate` aceita `look.ink`; `uv run pytest` cobre o schema.
- `cd render && npx tsc --noEmit` passa.
- `node scripts/check-render.mjs --style isometric-pastel`: still de cada cena com cobertura vertical do conteúdo >= 70% no `flow`, nenhuma faixa vazia > 25% do quadro, fundo claro (luminância > 0.8) com tema `forge` e pelo menos 3 cores da paleta.
- Manual: quadros de `title`, `flow`, `list`, `highlight` e `cta` do clip-05, tema forge.
