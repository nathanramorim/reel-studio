# feat-03-09-variantes-regionais-glossario — Glossário com variantes de pronúncia regional

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda; transcrição local).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Glossário | `core/glossary.py` | mapa `errado -> certo`, uma chave por variante | estender | Aceita várias variantes por termo |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, ARQ-06, DUP-01, TST-01

## Contexto do defeito
- **Origem:** `feat-03-03-glossario-correcoes`.
- **Causa-raiz:** Cada variante regional exige uma entrada própria no `correcoes.json`, repetindo o valor.
- **Evidência:** `checaja`, `fitres` e outras grafias do mesmo termo ficam espalhadas e fáceis de esquecer.

## Escopo
- Chave com variantes separadas por `|` (`"checaja|checage|checajem": "checagem"`), cada uma casada com as regras da `03-03` (palavras inteiras, sem caixa nem pontuação).
- Conflito (mesma variante com dois valores) é erro claro com o arquivo e a variante (`SEG-01`).
- O limite de 2000 entradas conta variantes.
- Contrato do `correcoes.json` documentado na skill e no README (`ARQ-06`); `checaja` entra no exemplo.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_glossary.py -k variantes`: `a|b|c -> x` corrige as três; conflito é rejeitado; limite conta variantes; `checaja -> checagem` corrige `words` e `text`.
- `uv run pytest && uv run ruff check` passam.
