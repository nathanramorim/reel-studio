---
description: Gera reels verticais a partir de um vídeo gravado, no modo corte ou VSL animado.
argument-hint: "[arquivo de vídeo]"
---

Gere o reel seguindo a skill `reel-studio`.

- Entrada: `$ARGUMENTS` — um vídeo, um arquivo de **conteúdo** (texto ou markdown) ou uma **ideia** livre (vazio = pergunte qual das três).
- A CLI está em `${CLAUDE_PLUGIN_ROOT}/engine` (`uv run reel-studio ...`) e o render em `${CLAUDE_PLUGIN_ROOT}/render`.
- Siga o passo a passo da skill: pergunte modo, tema e estilo; mostre o plano (cortes ou cenas) e espere o "sim" antes de gerar o vídeo final. Não faça commit.
- Voz: a original quando há vídeo; voz gerada só com `--voice clone --voice-ref ... --confirm-own-voice` e só da própria pessoa. Sem voz, a trilha liga sozinha.
