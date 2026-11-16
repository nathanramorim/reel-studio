# Catálogo de Conceitos e Contratos (`DUP-01`) — reel-studio

| Conceito | Dono | Entidade | Contrato público | Observação |
| --- | --- | --- | --- | --- |
| Pasta do vídeo e cache | `core/project.py` | `Project` | `Project.open(video)` | Hash do arquivo identifica o vídeo |
| Transcrição | `core/transcribe.py` | `transcript.json` | `contracts/transcript.schema.json` | Segmentos e palavras com tempo |
| Texto para o LLM | `core/compact.py` | — | `compact(transcript)` | Única forma de enviar transcrição |
| Chamada ao LLM | `core/llm.py` | `LLMClient` | `complete_json(system, user)` | Única porta de rede |
| Cortes | `core/suggest.py` | `clips.json` | `contracts/clips.schema.json` | Modo corte |
| Cenas | `core/script.py` | `scenes.json` | `contracts/scenes.schema.json` | Modo VSL |
| Tema | `themes/*.json` | — | `contracts/theme.schema.json` | Marca |
| Estilo | `styles/*/style.json` | — | `contracts/style.schema.json` | Linguagem visual e tipos de cena |
| Validação | `core/contracts.py` | — | `load(kind, path)` | Fonte única de schemas |
