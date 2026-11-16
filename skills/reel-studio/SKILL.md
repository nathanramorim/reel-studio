---
name: reel-studio
description: Use para transformar um vídeo já gravado em reel vertical para Instagram, no modo corte ou VSL animado, aplicando um tema (marca) e um estilo visual. Ative quando pedirem "reel", "corte para Instagram", "VSL", "transcrever vídeo", "extrair voz/áudio", ou colarem um arquivo de vídeo pedindo para virar conteúdo curto.
---

# reel-studio

Transforma um vídeo gravado em reel 9:16. O LLM nunca vê vídeo ou áudio: só a transcrição, compactada e enviada em **uma chamada** por etapa. Tudo roda local até o render.

## Dois modos

| Modo | Quando | Comando final |
|---|---|---|
| **Corte** | Vídeo e áudio estão bons | `cut` recorta o trecho real |
| **VSL** | Vídeo ou áudio ruim, ou quer um visual diferente | `script` + `render` geram animação |

## Passo a passo

1. **Pergunte o que falta**, uma vez: modo (corte ou VSL), tema (`uv run reel-studio list` em `${CLAUDE_PLUGIN_ROOT}/engine` mostra os disponíveis) e, no modo VSL, o estilo.
2. **Extraia e transcreva** (sempre, os dois modos precisam):
   ```
   cd ${CLAUDE_PLUGIN_ROOT}/engine
   uv run reel-studio extract VIDEO
   uv run reel-studio transcribe VIDEO
   ```
   Se faltar o extra, rode `uv sync --extra transcribe` (e `--extra voice` se o áudio tiver ruído de fundo, antes do extract com `--voice-only`).
3. **Modo corte — você mesmo gera o JSON, sem chave e sem chamada de rede nova:**
   ```
   uv run reel-studio prompt-suggest VIDEO --max 5
   ```
   Isso imprime o system e a transcrição compactada. Leia, pense como o prompt pede e **escreva você mesmo** o JSON `{"clips": [...]}` num arquivo (ex.: `cortes.json`, com `Write`). Depois:
   ```
   uv run reel-studio save-clips VIDEO --file cortes.json --max 5
   ```
   Mostre os cortes salvos (hora e gancho) e abra `VIDEO.reel/clips.json` para a pessoa aprovar ou editar. Só depois do "sim":
   ```
   uv run reel-studio cut VIDEO --theme TEMA
   ```
4. **Modo VSL — mesma lógica.** Veja `references/estilos.md` para escolher o estilo certo pelo tipo de conteúdo.
   ```
   uv run reel-studio prompt-script VIDEO --style ESTILO
   ```
   Escreva o JSON `{"scenes": [...]}` (ex.: `roteiro.json`) e grave:
   ```
   uv run reel-studio save-scenes VIDEO --style ESTILO --theme TEMA --file roteiro.json
   ```
   Mostre as cenas e espere o "sim" antes de:
   ```
   uv run reel-studio render VIDEO --theme TEMA
   ```
   Na primeira vez, `cd ${CLAUDE_PLUGIN_ROOT}/render && npm install` (demora, avise antes).
5. **Sem Claude Code, ou querendo automatizar sem agente no loop:** troque `prompt-suggest`/`save-clips` por `suggest` direto (idem `prompt-script`/`save-scenes` por `script`), com `OPENROUTER_API_KEY` no `.env`. Esse caminho existe só para automação fora de uma sessão com agente.
6. **Nunca gere o vídeo final sem aprovação** do `clips.json` ou do `scenes.json`.
7. **Sem tema que combine?** Veja `references/criar-tema.md`.
8. **Problema comum?** Veja `references/resolucao-de-problemas.md` antes de tentar de novo.

## Regras

- O LLM só recebe texto da transcrição, nunca mídia.
- Dentro do Claude Code, você mesmo gera `clips.json`/`scenes.json` a partir do prompt — não chame o OpenRouter nem peça chave à pessoa; isso só vale no caminho de automação (regra 5).
- Um reel por vez; não encadeie etapas sem mostrar o resultado.
- Linguagem simples, em português do Brasil.
- Nunca invente cortes ou cenas fora do que a transcrição sustenta.
- Não faça commit nem push, a menos que a pessoa peça.
