# Módulos — reel-studio

| Módulo | Onde | Responsabilidade |
|---|---|---|
| CLI | `engine/src/reel_studio/cli.py` | Borda: argumentos, validação, saída |
| Projeto | `core/project.py` | Pasta de trabalho por vídeo (hash), caminhos e cache |
| Áudio | `core/audio.py` | Extrair áudio e isolar voz |
| Transcrição | `core/transcribe.py` | Whisper local para `transcript.json` |
| Compactação | `core/compact.py` | Transcrição para texto mínimo enviado ao LLM |
| LLM | `core/llm.py` | Única porta de saída para o OpenRouter |
| Sugestão | `core/suggest.py` | Gera `clips.json` (modo corte) |
| Roteiro | `core/script.py` | Gera `scenes.json` (modo VSL) |
| Legenda | `core/captions.py` | Gera `.ass` com os tokens do tema |
| Corte | `core/cut.py` | Recorta, enquadra em 9:16 e queima legenda |
| Contratos | `core/contracts.py` + `contracts/` | Carregar e validar JSON |
| Render | `render/` | Remotion: cenas por estilo e tema |
| Plugin | `skills/`, `commands/` | Interface para o Claude Code |
