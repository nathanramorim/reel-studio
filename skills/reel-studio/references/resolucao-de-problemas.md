# Resolução de problemas

| Sintoma | Causa provável | Ação |
|---|---|---|
| Não sei o que falta instalar | Primeiro uso | `sh scripts/bootstrap.sh` (macOS e Linux) ou `powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1` (Windows), na raiz do reel-studio: mostra cada item e o comando do seu sistema; `uv run scripts/requisitos.py instalar <item>` instala com o seu ok |
| `'ffmpeg' não encontrado` | Não instalado | `uv run scripts/requisitos.py instalar ffmpeg` (macOS com Homebrew: `brew install ffmpeg-full`; Linux: pacote `ffmpeg` da distro; Windows: `winget install --id Gyan.FFmpeg -e`) |
| `Transcrever precisa do extra 'transcribe'` | Faltou instalar | `uv run scripts/requisitos.py instalar extra-transcribe` (ou `cd engine && uv sync --python 3.12 --inexact --extra transcribe`) |
| `TypeError: open() got an unexpected keyword argument 'metadata_errors'` no `transcribe` | `av` 19 é incompatível com o faster-whisper | `cd engine && uv sync --extra transcribe` (o extra fixa `av<17`) |
| `Este ffmpeg não tem o filtro 'ass'` | ffmpeg sem libass | macOS com Homebrew: `brew install ffmpeg-full` e `brew link --overwrite --force ffmpeg-full` (sob Rosetta, `arch -arm64 brew ...`); MacPorts: `port install ffmpeg`; Linux: pacote `ffmpeg` da distro; Windows: `winget install --id Gyan.FFmpeg -e` |
| Whisper erra termos ou sotaque | Modelo pequeno, sem vocabulário | `transcribe --model medium` e `correcoes.json` com variantes (`"checaja\|checage": "checagem"`) |
| `Isolar voz precisa do extra 'voice'` | Faltou instalar | `uv run scripts/requisitos.py instalar extra-voice` (Windows arm64 não tem PyTorch: use o WSL) |
| `Defina OPENROUTER_API_KEY` | Só acontece com `suggest`/`script` (caminho de automação) | Dentro do Claude Code, use `prompt-suggest`/`save-clips` ou `prompt-script`/`save-scenes`, que não precisam de chave |
| JSON que você escreveu foi rejeitado | Saiu do contrato (`clips.schema.json`/`scenes.schema.json`) | Leia o erro, que aponta o campo; ajuste e rode `save-clips`/`save-scenes` de novo |
| `Instale o render uma vez` | Remotion sem dependências | `cd render && npm install` (primeira vez demora) |
| Download do Chrome do Remotion falha | Rede bloqueada (sandbox corporativo) | Rode `render` fora do sandbox, numa máquina com rede livre |
| Tipos de cena fora do estilo | O LLM tentou um tipo não suportado | Rode `script` de novo; se persistir, abra uma issue |
