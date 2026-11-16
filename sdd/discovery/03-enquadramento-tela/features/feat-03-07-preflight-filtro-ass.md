# feat-03-07-preflight-filtro-ass — `cut` falha tarde com `Unknown filter 'ass'`

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda; transcrição local).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Checagem de ffmpeg | `core/proc.py` `require_bin` | só confere o binário | estender | Adiciona `has_filter("ass")` |
| Orientação de instalação | `proc.FFMPEG_HINT` | `brew install ffmpeg` | estender | Passa a citar `ffmpeg-full` |
| Iniciativa 02 | `sdd/discovery/02-setup-ffmpeg-libass` (branch `feat/02-…`, não mesclada) | `doctor` e instalação automática | reusar a decisão | Esta feature é só o preflight do `cut`; a 02 remove o `feat-02-03` equivalente |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05, DUP-03, TST-01

## Contexto do defeito
- **Origem:** `feat-01-04-cortar-legenda`.
- **Causa-raiz:** O `cut` só descobre a falta do filtro `ass` (libass) quando o ffmpeg já está rodando; o `brew install ffmpeg` gera um binário sem libass.
- **Evidência:** `Unknown filter 'ass'` e nenhum vídeo gerado.

## Escopo
- Antes de cortar, `cut` roda `ffmpeg -filters` (lista de argumentos) e confere `ass`; se faltar, para com erro e orientação: `brew install ffmpeg-full` (macOS; sob Rosetta, `arch -arm64 brew install ffmpeg-full`), `winget` no Windows e o motivo (a legenda do tema precisa de libass).
- Detecta Rosetta por `sysctl -n sysctl.proc_translated` e só então sugere `arch -arm64`.
- `--dry-run` não exige o filtro (`ARQ-05`).
- Não instala nada: a instalação automática fica na iniciativa 02.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_cut.py -k preflight`: com `ffmpeg -filters` sem `ass` o `cut` falha antes de qualquer corte, com a mensagem de `ffmpeg-full`; com o filtro, segue; sob Rosetta simulado, a mensagem traz `arch -arm64`; `--dry-run` não falha.
- `uv run pytest && uv run ruff check` passam.
