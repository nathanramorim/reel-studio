---
description: Gera reels verticais a partir de um vídeo gravado, no modo corte ou VSL animado.
argument-hint: "[arquivo de vídeo]"
---

Gere o reel seguindo a skill `reel-studio`.

- Vídeo: `$ARGUMENTS` (vazio = pergunte qual arquivo).
- A CLI está em `${CLAUDE_PLUGIN_ROOT}/engine` (`uv run reel-studio ...`) e o render em `${CLAUDE_PLUGIN_ROOT}/render`.
- Siga o passo a passo da skill: pergunte modo, tema e estilo; mostre o plano (cortes ou cenas) e espere o "sim" antes de gerar o vídeo final. Não faça commit.
