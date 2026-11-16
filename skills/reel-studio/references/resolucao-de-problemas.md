# Resolução de problemas

| Sintoma | Causa provável | Ação |
|---|---|---|
| `'ffmpeg' não encontrado` | Não instalado | `brew install ffmpeg` (macOS) ou `winget install ffmpeg` (Windows) |
| `Transcrever precisa do extra 'transcribe'` | Faltou instalar | `cd engine && uv sync --extra transcribe` |
| `Isolar voz precisa do extra 'voice'` | Faltou instalar | `cd engine && uv sync --extra voice` |
| `Defina OPENROUTER_API_KEY` | Só acontece com `suggest`/`script` (caminho de automação) | Dentro do Claude Code, use `prompt-suggest`/`save-clips` ou `prompt-script`/`save-scenes`, que não precisam de chave |
| JSON que você escreveu foi rejeitado | Saiu do contrato (`clips.schema.json`/`scenes.schema.json`) | Leia o erro, que aponta o campo; ajuste e rode `save-clips`/`save-scenes` de novo |
| `Instale o render uma vez` | Remotion sem dependências | `cd render && npm install` (primeira vez demora) |
| Download do Chrome do Remotion falha | Rede bloqueada (sandbox corporativo) | Rode `render` fora do sandbox, numa máquina com rede livre |
| Tipos de cena fora do estilo | O LLM tentou um tipo não suportado | Rode `script` de novo; se persistir, abra uma issue |
