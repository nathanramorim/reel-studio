# feat-03-05-fixar-av-transcribe — `transcribe` quebra com av 19

## Modelo do módulo
enxuto (só dependência e documentação)

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda; transcrição local).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Extra `transcribe` | `engine/pyproject.toml` | `faster-whisper>=1.0`, sem teto para `av` | estender | Fixar `av` compatível |

## Dependências novas
Nenhuma nova; restringe `av` (já transitiva de `faster-whisper`). Consultar context7 com a versão exata (`SEG-07`).

## Rules e IDs da Constituição Aplicáveis
ARQ-04, SEG-07, TST-01

## Contexto do defeito
- **Origem:** `feat-01-02-transcrever`.
- **Causa-raiz:** `faster-whisper` 1.2.1 é incompatível com `av` 19; o `uv.lock` resolve `av` 19.0.2 em Python ≥ 3.12.
- **Evidência:** `TypeError: open() got an unexpected keyword argument 'metadata_errors'` em `transcribe`.

## Escopo
- Extra `transcribe` passa a declarar `av<17`, e o `uv.lock` é regerado.
- `resolucao-de-problemas.md` ganha a linha do erro.

## Critérios de Aceitação Executáveis
- `cd engine && uv sync --extra transcribe && uv run python -c "import av; assert int(av.__version__.split('.')[0]) < 17"`.
- `uv run pytest tests/test_transcribe.py -k av`: o `pyproject.toml` contém o teto `av<17` no extra `transcribe`.
- `uv run reel-studio transcribe <vídeo curto>` conclui sem `TypeError` (manual).
- `uv run pytest && uv run ruff check` passam.
