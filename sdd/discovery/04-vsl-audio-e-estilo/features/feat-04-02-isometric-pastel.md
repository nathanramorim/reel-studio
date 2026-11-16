# feat-04-02-isometric-pastel — `isometric-pastel`: animação isométrica nas cores do tema, quadro bem usado

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; `SceneRenderer` único ponto `type -> componente`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Estilo | `styles/isometric-pastel/style.json` | `background: theme`, paleta hex própria usada só em borda | estender | Fica `theme`; a paleta passa a ser tokens do tema |
| Cenas | `render/src/scenes/*` | componentes planos, iguais em todos os estilos | estender | Variante isométrica por estilo, num registro |
| Cores | `feat-04-05` (paleta e fundo do tema) | — | reusar | O estilo não traz cores; usa as do tema |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-06, DUP-01, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** O estilo só troca cores e borda; não há projeção isométrica, a paleta pastel quase não aparece, o fundo vem do tema (preto no `forge`) e o conteúdo fica no centro com muito espaço vazio.
- **Evidência:** Quadro do `flow` no clip-05: quatro caixas escuras empilhadas no meio de 1080×1920, setas verticais, fundo `#0d0f14`.

## Escopo
- **Cores do design system do projeto (decisão do humano):** o estilo define só a animação e a forma; fundo, preenchimentos e texto vêm do tema (`feat-04-05`). `isometric-pastel` usa `background: theme` e nenhuma cor própria.
- Componente único `IsoSlab` (projeção de 30°, três tons por face: topo, lateral esquerda, lateral direita, sombra longa) preenchido com a paleta resolvida do tema, em ciclo.
- Variante do estilo por registro (`styleScenes`): o `SceneRenderer` continua único mapa `type -> componente` e escolhe a variante pelo `style.id`; estilos sem variante usam os componentes atuais.
- **`flow`:** os passos viram placas em escada diagonal pelo quadro (ocupa pelo menos 70% da altura útil), ligadas por setas ao longo dos eixos isométricos; número, rótulo grande e entrada em sequência.
- **`title`, `highlight`, `cta`:** a frase sobre uma placa grande flutuante, ocupando a largura útil; **`list`:** itens em placas empilhadas; **`compare`:** duas placas lado a lado.
- Margens de segurança de 80 px e conteúdo distribuído na altura, sem faixa vazia maior que 25% do quadro.

## Critérios de Aceitação Executáveis
- `cd engine && uv run reel-studio validate` e `uv run pytest` passam.
- `cd render && npx tsc --noEmit` passa.
- `node scripts/check-render.mjs --style isometric-pastel`: still de cada cena com cobertura vertical do conteúdo >= 70% no `flow`, nenhuma faixa vazia > 25% do quadro, fundo igual ao do tema `forge` (`#0d0f14` com o brilho) e preenchimentos com as cores dos tokens do tema (`#4f8ef7`, `#8aa4ff`, `#3ecf8e`).
- Manual: quadros de `title`, `flow`, `list`, `highlight` e `cta` do clip-05, tema forge.
