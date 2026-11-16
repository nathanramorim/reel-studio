# Resolução de problemas

| Sintoma | Causa provável | Ação |
|---|---|---|
| `'ffmpeg' não encontrado` | Não instalado | `brew install ffmpeg` (macOS) ou `winget install ffmpeg` (Windows) |
| `Transcrever precisa do extra 'transcribe'` | Faltou instalar | `cd engine && uv sync --extra transcribe` |
| `Isolar voz precisa do extra 'voice'` | Faltou instalar | `cd engine && uv sync --extra voice` |
| `Defina OPENROUTER_API_KEY` | Chave não configurada | Crie `.env` na raiz do repo clonado, com `OPENROUTER_API_KEY=...` (nunca comite) |
| `O modelo não devolveu JSON válido` | Falha passageira do modelo | Rode `suggest` ou `script` de novo |
| `Instale o render uma vez` | Remotion sem dependências | `cd render && npm install` (primeira vez demora) |
| Download do Chrome do Remotion falha | Rede bloqueada (sandbox corporativo) | Rode `render` fora do sandbox, numa máquina com rede livre |
| Tipos de cena fora do estilo | O LLM tentou um tipo não suportado | Rode `script` de novo; se persistir, abra uma issue |
