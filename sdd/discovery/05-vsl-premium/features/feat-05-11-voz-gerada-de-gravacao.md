# feat-05-11-voz-gerada-de-gravacao — Voz gerada a partir de gravação (clone local)

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima. ADR-0003 (a criar nesta feature): escolha do modelo de voz.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Transcrição | `core/transcribe.py` | Whisper local com tempos de palavra | reusar | Alinha o áudio gerado |
| Áudio | `core/audio.py` | extrai e isola voz | reusar | Fonte da amostra |
| Duração das cenas | `core/render.durations` | duração efetiva | estender | A cena segue o áudio gerado |
| Extras opcionais | `engine/pyproject.toml` (`transcribe`, `voice`, `vision`) | extras do uv | estender | Novo extra `tts` |
| Modelo de voz | `resemble-ai/chatterbox` (MIT, clona de amostra, português e pt-BR, `cpu`/`mps`/`cuda`, marca d'água) | candidato | decidir na ADR-0003 | Confirmar versão, licença dos pesos e qualidade |

## Dependências novas
Extra opcional `tts` (`ARQ-04`): candidato Chatterbox. Consultar o context7 com a versão exata e confirmar a licença dos pesos antes de implementar (`SEG-07`). O modelo é baixado uma vez, na instalação, nunca durante o render.

## Rules e IDs da Constituição Aplicáveis
ARQ-04, SEG-03, SEG-05, SEG-07, DUP-03, TST-01

## Escopo
- `core/voice.py`: `reference(origem, workdir)` escolhe a melhor amostra de 10 a 30 s (fala contínua, sem sobreposição, melhor relação sinal-ruído) e grava `voice-ref.wav` na pasta do vídeo; `synthesize(cenas, ref, lang)` gera um áudio por cena com o modelo, por import tardio e dispositivo automático.
- `render --voice clone --voice-ref ARQUIVO --confirm-own-voice`: a confirmação de que é a própria voz (ou autorizada) é obrigatória, sem prompt interativo; sem a flag, erro claro. Sem referência, sem voz.
- A duração de cada cena passa a ser a do áudio gerado; os tempos de palavra vêm de transcrever esse áudio com o Whisper local (alimenta `feat-05-06` e a legenda).
- A marca d'água do modelo é mantida; amostra e áudio ficam na pasta do vídeo, nunca em log ou rede (`SEG-05`).
- `sdd/spec/adr/adr-0003-voz-gerada.md` com a decisão do modelo; `uv sync --extra tts` documentado.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_voice.py -k amostra`: escolhe o trecho de fala contínua e limpa e respeita 10 a 30 s.
- `uv run pytest tests/test_voice.py -k consentimento`: sem `--confirm-own-voice` falha; sem `--voice-ref` não gera voz.
- `uv run pytest tests/test_voice.py -k duracao`: com sintetizador simulado, a cena dura o áudio gerado e os tempos de palavra vêm da transcrição simulada (os testes não baixam o modelo).
- `uv run pytest && uv run ruff check` passam.
- Manual (C12): VSL do clip-05 com a voz gerada a partir da gravação 14.33.02; medir o tempo e avaliar o pt-BR.
