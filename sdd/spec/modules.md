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

## Isolar voz
- **Onde:** `core/audio.py` (extra `voice`, demucs)
- **Responsabilidade:** Extrair áudio (ffmpeg) e, se pedido, isolar a voz do fundo

## Glossário
- **Onde:** `core/glossary.py`
- **Responsabilidade:** Corrige em memória termos que o Whisper erra (`correcoes.json`), antes da legenda e do prompt

## Quadros
- **Onde:** `core/frames.py` (extra `vision`, OpenCV)
- **Responsabilidade:** Rosto e região com atividade para o enquadramento `fill`/`zoom`/`fit`

## Paleta e contraste
- **Onde:** `core/palette.py`, `core/contrast.py`
- **Responsabilidade:** Tokens do tema viram cores do estilo; contraste WCAG das cores sobre o fundo

## Overlay
- **Onde:** `core/overlay.py`
- **Responsabilidade:** Componentes Remotion transparentes compostos sobre o corte intacto

## VSL
- **Onde:** `core/render.py`
- **Responsabilidade:** Entrega `scenes.json` + tema + estilo ao Remotion, com legenda e áudio original

## Infraestrutura
- **Onde:** `core/paths.py`, `core/proc.py`, `core/errors.py`
- **Responsabilidade:** Caminhos de contratos, temas e estilos; processos externos sem shell; erros prontos para o usuário

## Contratos
- **Onde:** `core/contracts.py` + `contracts/`
- **Responsabilidade:** Carregar e validar JSON

## Render
- **Onde:** `render/`
- **Responsabilidade:** Remotion: cenas por estilo e tema

## Temas e estilos
- **Onde:** `themes/*.json`, `styles/<estilo>/`
- **Responsabilidade:** Marca (cores, fontes, logo, CTA) e linguagem visual, eixos independentes

## Plugin
- **Onde:** `.claude-plugin/`, `skills/reel-studio/`, `commands/`; adaptadores `.agents/skills/reel-studio/` (agy) e `AGENTS.md` (Codex)
- **Responsabilidade:** Interface para Claude Code, agy e Codex, com uma só fonte de skill (`DUP-10`)
