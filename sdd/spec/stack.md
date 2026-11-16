# Stack — reel-studio

## Dependências

| Camada | Escolha | Versão | Licença | Motivo |
|--------|---------|--------|---------|--------|
| Runtime | Python | >=3.11 | PSF | Motor |
| Gerenciador | uv | atual | MIT/Apache | Padrão do autor |
| CLI | typer | >=0.12 | MIT | Comandos simples |
| HTTP | httpx | >=0.27 | BSD | Chamada ao OpenRouter, só no caminho de automação (sem agente) |
| Transcrição | faster-whisper | >=1.0 (extra `transcribe`) | MIT | Local |
| Isolar voz | demucs | >=4.0 (extra `voice`) | MIT | Local, opcional |
| Mídia | ffmpeg | sistema | LGPL/GPL conforme build | Corte e legenda |
| Render | Remotion | 4.x | Remotion License (grátis até 3 pessoas) | Cenas animadas |
| Render | Manim Community | >=0.18 (extra `manim`) | MIT | Estilo matemático |
| Lip sync | rhubarb-lip-sync | binário | MIT | Avatar estilizado (fase 3) |

## Layout do projeto
```
.claude-plugin/        plugin.json e marketplace.json
skills/reel-studio/    SKILL.md + references/ (lidas sob demanda)
commands/              /gerar-reel, /transcrever, /extrair-voz
contracts/             JSON Schemas: transcript, clips, scenes, theme, style
themes/                tokens de marca (pessoal, busize, forge, exemplo)
styles/                estilos visuais (style.json + style.md)
engine/                CLI Python (uv)
  src/reel_studio/cli.py     borda
  src/reel_studio/core/      domínio
render/                Remotion (TS)
sdd/                   Forge SDD
```
