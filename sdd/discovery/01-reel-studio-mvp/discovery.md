# Discovery 01 — reel-studio MVP

## Problema
Vídeos explicando processos ficam parados por falta de ferramenta para virar reel. Às vezes o vídeo ou o áudio não estão bons, e SaaS de corte manda o conteúdo para nuvem de terceiro.

## Para quem
Criadores técnicos que gravam explicações e querem publicar no Instagram com a própria marca. Primeiro usuário: o autor (temas pessoal, Busize e Forge SDD).

## Jornada
1. Instala o plugin pelo Claude Code.
2. Roda `/gerar-reel aula.mp4`.
3. A skill transcreve local, sugere cortes ou roteiro e mostra para aprovação.
4. A pessoa ajusta o JSON se quiser e aprova.
5. Sai o `.mp4` vertical no estilo e na marca escolhidos.

## Regras de negócio
- O LLM nunca recebe mídia, só texto compactado.
- Nada é renderizado sem aprovação do `clips.json` ou do `scenes.json`.
- Corte respeita frases completas (início e fim em limite de segmento).
- Reels entre 15 e 60 segundos por padrão.
- Tema e estilo são independentes.

## Escopo
**Dentro:** extract, transcribe, suggest, cut (modo corte); script e render com 3 estilos SVG (modo VSL); 3 temas + exemplo; plugin.
**Fora (fase 3):** estilo Manim renderizado, avatar com lip sync, TTS com clone de voz, publicação automática no Instagram.

## Riscos
| Risco | Mitigação |
|---|---|
| Licença Remotion para empresas | Documentar; modo corte não depende dele |
| Whisper lento em CPU | Modelo `small` por padrão, cache por hash |
| Corte no meio do raciocínio | Modo semiautomático e limite de segmento |
| Vazamento de conteúdo | Só texto sai; provedor escolhido pelo usuário |
