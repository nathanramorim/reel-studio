# Módulos — reel-studio

Limites de contexto: a CLI é a borda (`ARQ-01`); `core/` é o domínio e não conhece a borda (`ARQ-10`).

## CLI
- **Onde:** `engine/src/reel_studio/cli.py`
- **Responsabilidade:** Borda: argumentos, validação, saída

## Projeto
- **Onde:** `core/project.py`
- **Responsabilidade:** Pasta de trabalho por vídeo (hash), caminhos e cache

## Áudio
- **Onde:** `core/audio.py`
- **Responsabilidade:** Extrair áudio e isolar voz

## Transcrição
- **Onde:** `core/transcribe.py`
- **Responsabilidade:** Whisper local para `transcript.json`

## Compactação
- **Onde:** `core/compact.py`
- **Responsabilidade:** Transcrição para texto mínimo enviado ao LLM

## LLM
- **Onde:** `core/llm.py`
- **Responsabilidade:** Única porta de saída para o OpenRouter (caminho de automação)

## Sugestão
- **Onde:** `core/suggest.py`
- **Responsabilidade:** `prompt()` monta o prompt para o agente; `normalize()` valida o JSON e gera `clips.json`; `suggest()` chama o OpenRouter (automação)

## Roteiro
- **Onde:** `core/script.py`
- **Responsabilidade:** `prompt()` monta o prompt para o agente; `normalize()` valida o JSON e gera `scenes.json`; `script()` chama o OpenRouter (automação)

## Legenda
- **Onde:** `core/captions.py`
- **Responsabilidade:** Gera `.ass` com os tokens do tema

## Corte
- **Onde:** `core/cut.py`
- **Responsabilidade:** Recorta, enquadra em 9:16 e queima legenda

## Contratos
- **Onde:** `core/contracts.py` + `contracts/`
- **Responsabilidade:** Carregar e validar JSON

## Render
- **Onde:** `render/`
- **Responsabilidade:** Remotion: cenas por estilo e tema

## Plugin
- **Onde:** `skills/`, `commands/`
- **Responsabilidade:** Interface para o Claude Code
