# AGENTS.md — reel-studio

Este repositório é o reel-studio: transforma vídeos já gravados em reels 9:16 para Instagram (corte real ou VSL animado), aplicando tema (marca) e estilo visual. Veja `README.md` para a visão geral e `sdd/` para a arquitetura (Forge SDD).

## Como operar aqui

Fonte única da skill de geração de reels: `skills/reel-studio/SKILL.md` e `skills/reel-studio/references/`. Antes de qualquer tarefa de reel (cortar vídeo, gerar VSL, aplicar tema, escolher estilo), leia esse arquivo e siga os passos dele. `RAIZ`, mencionado ali, é a raiz deste repositório (onde está este `AGENTS.md`); rode o motor em `RAIZ/engine` com `uv run reel-studio ...` e o render em `RAIZ/render` com `npx remotion ...`.

## Regras do projeto

- O LLM (você) só recebe texto da transcrição, nunca vídeo ou áudio.
- Você mesmo gera `clips.json`/`scenes.json` a partir do prompt de `prompt-suggest`/`prompt-script` — não chame o OpenRouter; isso é só para automação sem agente (veja a skill).
- Nunca gere o vídeo final (`cut`/`render`) sem a pessoa aprovar `clips.json` ou `scenes.json` primeiro.
- Siga o Forge SDD: nunca comite em `main`; uma branch por iniciativa (`sdd/memory/constitution.md`, `sdd/discovery/`).
