# feat-03-08-modelo-e-initial-prompt — Transcrição: modelo maior e vocabulário no Whisper

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda; transcrição local).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Transcrição | `core/transcribe.py`, `cli.transcribe` | `--model small`, sem `initial_prompt`, cache sem registrar o modelo | estender | Mesmo dono (Transcrição) |
| Vocabulário | `core/glossary.py` (`feat-03-03`), `themes/*.json` | chaves e valores do glossário | reusar | Os termos certos alimentam o prompt |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, ARQ-05, ARQ-10, DUP-01, TST-01

## Contexto do defeito
- **Origem:** `feat-01-02-transcrever`.
- **Causa-raiz:** `small` e nenhuma dica de vocabulário: o Whisper erra termos do domínio e o sotaque regional (autor mineiro).
- **Evidência:** "checagem" saiu como "checaja" na legenda.

## Escopo
- `--model` aceita `tiny|base|small|medium|large-v3` (padrão `small`; `medium` e `large-v3` são os recomendados para sotaque); valor fora da lista é rejeitado na borda (`SEG-01`). O padrão também pode vir de `REEL_WHISPER_MODEL`.
- `initial_prompt` montado automaticamente: termos certos do glossário (valores) + campo opcional `vocabulary` (lista) do tema, sem repetir, limitado a ~200 tokens (~800 caracteres); `--prompt` permite texto extra.
- O `transcript.json` registra `model` e `initial_prompt`; se o cache foi feito com outro modelo ou prompt, o `transcribe` avisa e refaz.
- O cache de áudio e do vídeo continua por hash.

## Critérios de Aceitação Executáveis
- `uv run pytest tests/test_transcribe.py -k modelo`: modelo inválido rejeitado; `large-v3` repassado ao `WhisperModel`; `REEL_WHISPER_MODEL` respeitado.
- `uv run pytest tests/test_transcribe.py -k prompt`: prompt contém os termos do glossário e do tema, sem repetição e dentro do limite.
- `uv run pytest tests/test_transcribe.py -k cache`: mudar modelo ou prompt invalida o cache; igual reaproveita.
- `uv run pytest && uv run ruff check` passam.
- Manual: `transcribe --model medium` no vídeo 14.33.02 e conferir "checagem".
