# feat-04-04-contraste-estilo-tema — Cor do texto pelo fundo do estilo (contraste mínimo)

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes e combináveis). Dono do cálculo: `core/` (domínio); o render só lê as cores já resolvidas (`DUP-01`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Props do render | `core/render.props` | repassa o tema sem alterar | estender | Passa a entregar o tema com cores resolvidas |
| Cores nas cenas | `render/src/scenes/*` | usam `theme.colors.text/muted/surface/accent` | reusar | Sem mudar os componentes: recebem as cores já ajustadas |
| Fundo do estilo | `style.json` `background`/`look.bg` | `own` com cor sólida ou gradiente (`flat-vector-science`) | reusar | Base do cálculo |
| Override de texto | `look.ink` (`feat-04-02`) | cor de texto opcional do estilo | reusar | Vence o cálculo automático quando existir |
| Contraste | — | nada | criar | `core/contrast.py`, dono do conceito (`DUP-01`) |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, ARQ-05, ARQ-06, ARQ-10, DUP-01, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-06-render-remotion`.
- **Causa-raiz:** os estilos com fundo próprio (`own`) usam as cores do tema, pensadas para o fundo do tema. Tema escuro sobre fundo claro dá texto claro sobre claro.
- **Evidência:** `vsl-whiteboard-explainer-forge.mp4` (fundo `#f7f7f4`, texto `#e9ecf4`): `list`, `highlight` e `cta` ilegíveis; só o `title` e as caixas do `flow` aparecem. O mesmo vale para `isometric-pastel` (`#f6f1ea`) com o `forge`, e para temas claros (`busize`) sobre `manim-style-math` e `flat-vector-science`.

## Escopo
- **Resolução única:** `core/contrast.py` calcula a razão de contraste WCAG 2.x entre cores. `core/render.props` entrega o tema com `colors` resolvidos para o fundo efetivo (do estilo `own` ou do tema); os componentes não mudam.
- **Fundo efetivo:** cor sólida, ou o pior caso entre as paradas de um gradiente (`flat-vector-science`).
- **Regras:**
  - `text` precisa de contraste >= 4,5 com o fundo; `muted` >= 4,5; `accent` e `accent2` >= 3 (texto grande e elementos de interface).
  - Se a cor do tema não atinge o mínimo, escolhe a melhor entre `look.ink` (se houver), o escuro do tema (`bg`) e o claro do tema (`text`); `accent` é escurecido ou clareado em passos até atingir o mínimo, mantendo o matiz.
  - `surface` é derivada do fundo efetivo (alguns pontos mais escura ou mais clara), para as caixas do `flow` e as placas não ficarem invertidas.
- **Aviso:** quando alguma cor foi ajustada, o `render` imprime `contraste: tema <id> sobre estilo <id>: cores ajustadas (text, surface, accent)`; sem ajuste, não imprime nada. `--dry-run` imprime o aviso e não escreve (`ARQ-05`).
- **Sem ajuste quando já contrasta:** `forge` sobre `manim-style-math` (fundo preto) e `busize` sobre `whiteboard-explainer` ficam iguais.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_contrast.py`: razão WCAG correta para pares conhecidos (preto sobre branco 21, `#767676` sobre branco 4,54); gradiente usa o pior caso.
- `uv run pytest tests/test_render.py -k contraste`: para as 12 combinações de 3 temas escuros e claros com os 4 estilos, `text` e `muted` ficam >= 4,5 e `accent` >= 3 sobre o fundo efetivo; `forge` x `whiteboard-explainer` e `forge` x `isometric-pastel` trazem texto escuro; `forge` x `manim-style-math` não muda.
- `uv run pytest tests/test_render.py -k aviso`: o aviso aparece só quando houve ajuste.
- `cd engine && uv run pytest && uv run ruff check` passam.
- Manual (clip-05): `render --style whiteboard-explainer --theme forge`: `list`, `highlight` e `cta` legíveis.

## Observação
O áudio e a fonte pequena do mesmo relato (item 13) já são cobertos por `feat-04-03` (narração) e `feat-04-01` (fontes e escala), que valem para todos os estilos.
