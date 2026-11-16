# feat-03-06-flags-file-e-style — Doc manda `--file`/`--style`, CLI espera posicional

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda; transcrição local).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Comandos `save-clips`, `save-scenes` | `cli.py` | `file` e `style` posicionais | estender | Aceitar as flags documentadas e manter o posicional |
| Doc | `SKILL.md`, `README.md`, `commands/`, `resolucao-de-problemas.md` | usam `--file` e `--style` | reusar | Passa a valer como está |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-06, SEG-01, TST-01

## Contexto do defeito
- **Origem:** `feat-01-03-sugerir-cortes` e `feat-01-05-roteiro-cenas`.
- **Causa-raiz:** As funções declaram `file` (e `style`) como argumento posicional; a documentação em quatro lugares usa flags.
- **Evidência:** `save-clips VIDEO --file cortes.json` falha; só `save-clips VIDEO cortes.json` funciona.

## Escopo
- `save-clips` aceita `--file` e continua aceitando o posicional; `save-scenes` aceita `--file` e `--style` e continua aceitando os posicionais.
- Os dois juntos (flag e posicional) ou nenhum dão erro claro.
- A documentação passa a refletir os dois formatos.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_cli.py -k flags`: `save-clips VIDEO --file X`, `save-clips VIDEO X`, `save-scenes VIDEO --style S --file X` e o posicional funcionam; flag e posicional juntos falham com mensagem.
- `grep -rn "save-clips\|save-scenes" skills README.md commands` só traz formatos aceitos.
- `uv run pytest && uv run ruff check` passam.
