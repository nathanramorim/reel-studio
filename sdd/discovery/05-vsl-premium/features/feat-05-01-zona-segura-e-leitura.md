# feat-05-01-zona-segura-e-leitura — Zona segura da vertical e tempo de leitura

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Escala e margens | `render/src/scale.ts` | escala tipográfica 1080×1920 | estender | Constantes da zona segura ao lado da escala |
| Placas isométricas | `render/src/iso/` | conteúdo desce até ~y 1650 | estender | Reduzir a área útil à zona segura |
| Validação do roteiro | `core/script.normalize`, `check_sources` | valida `source` | estender | Valida o tempo de leitura |
| Legenda do corte | `core/captions.py` | `lower-third`, margem 560 | reusar sem alterar | Já cai dentro da zona segura; não muda |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, ARQ-05, DUP-03, TST-01

## Escopo
- `render/src/safeZone.ts`: topo 250, base 1536 e guarda direita de 140 px na metade de baixo; os componentes novos e as cenas do estilo isométrico usam essas constantes.
- `normalize` rejeita cena cuja `dur` seja menor que 0,3 s por palavra do texto exibido (`text`, `steps`, `items`) mais 0,4 s de entrada, com a mensagem apontando a cena e a duração mínima.
- A legenda do corte e o `.ass` do modo corte **não mudam**.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_script.py -k leitura`: cena curta demais é rejeitada; cena adequada passa; texto vazio não exige mínimo.
- `cd render && node scripts/check-render.mjs --safe-zone`: todo texto de cena de `isometric-pastel` fica entre y 250 e 1536 e fora dos 140 px da direita na metade de baixo.
- `cd engine && uv run pytest -k regressao`: o `.ass` e o comando de corte seguem iguais.
- `cd render && npx tsc --noEmit` e `cd engine && uv run pytest && uv run ruff check` passam.
