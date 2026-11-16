<p align="center">
  <img src="docs/banner.svg" alt="reel-studio: Seus vídeos, virando reels." width="100%">
</p>

<p align="center">
  <a href="https://github.com/nathanramorim/reel-studio/releases"><img alt="versão" src="https://img.shields.io/github/v/tag/nathanramorim/reel-studio?label=vers%C3%A3o&color=4f8ef7&labelColor=0d0f14"></a>
  <img alt="licença" src="https://img.shields.io/badge/licen%C3%A7a-MIT-4f8ef7?labelColor=0d0f14">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-plugin-4f8ef7?labelColor=0d0f14">
  <img alt="agy" src="https://img.shields.io/badge/agy-skill-4f8ef7?labelColor=0d0f14">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-AGENTS.md-4f8ef7?labelColor=0d0f14">
  <img alt="uv" src="https://img.shields.io/badge/Python-uv-4f8ef7?labelColor=0d0f14">
  <img alt="dados" src="https://img.shields.io/badge/dados-100%25%20locais-4f8ef7?labelColor=0d0f14">
</p>

<h3 align="center">Corte real ou VSL animado, na sua marca.<br>Tudo local; uma chamada de IA por vídeo.</h3>

---

## O que é

O **reel-studio** transforma um vídeo que você já gravou em um reel vertical para o Instagram. Dois modos: **corte**, que recorta o trecho real do vídeo, e **VSL**, que reescreve a fala como um roteiro curto e anima num dos estilos visuais.

A transcrição roda local (Whisper). O modelo de IA só vê o texto, nunca o vídeo nem o áudio. Dentro do Claude Code, é o próprio Claude que escolhe os cortes e escreve o roteiro — sem chave de API, sem chamada de rede extra. Fora do Claude Code, há um caminho de automação via OpenRouter. Nada é gerado sem você aprovar o corte ou o roteiro primeiro.

## Por que usar

| | |
|---|---|
| 🎬 **Dois modos** | Vídeo bom? Corta o real. Vídeo ou áudio ruim? Anima o roteiro. |
| 🔒 **Dados locais** | Mídia nunca sai da sua máquina; só texto compactado vai para a IA. |
| 🎨 **Sua marca** | Tema (cores, fonte, CTA) e estilo visual são independentes; combine como quiser. |
| 🧠 **Poucos tokens** | Cerca de 1 a 2 mil tokens por reel, numa chamada só. |
| 🧩 **Replicável** | Plugin do Claude Code: instala, usa o próprio tema, pronto. |

## Antes de começar

- **Python 3.11+** com [uv](https://docs.astral.sh/uv/).
- **ffmpeg** no PATH (`brew install ffmpeg` ou `winget install ffmpeg`).
- **Node.js 18+** (só para o modo VSL, que usa Remotion).
- **Um agente que lê skills** (Claude Code, agy/Antigravity ou Codex) para gerar cortes e roteiros sem chave de API. Sem nenhum deles, dá para automatizar com `OPENROUTER_API_KEY` (veja "Caminho de automação" abaixo).

## Instalação

### No Claude Code

```
/plugin marketplace add nathanramorim/reel-studio
/plugin install reel-studio@reel-studio
```

### No agy (Antigravity) ou Codex

```bash
git clone https://github.com/nathanramorim/reel-studio
cd reel-studio
cd engine && uv sync --extra transcribe
cd ../render && npm install   # só se for usar o modo VSL
```

Abra o agy ou o Codex **dentro da pasta `reel-studio`**: o agy encontra a skill em `.agents/skills/reel-studio/`, o Codex lê `AGENTS.md` na raiz. Os dois apontam para a mesma fonte, `skills/reel-studio/SKILL.md`.

## Como usar

No Claude Code, dentro de uma sessão com o plugin instalado:

```
/gerar-reel aula.mp4
```

A skill pergunta o modo, o tema e (no modo VSL) o estilo, mostra o plano e só gera o vídeo depois do seu "sim". Comandos extras: `/transcrever` e `/extrair-voz`.

No agy ou no Codex não há comando de barra: basta pedir em linguagem natural, ex. "gere um reel de aula.mp4 no modo corte, tema busize" — o agente lê a mesma skill e segue os mesmos passos.

Pela CLI, dentro de uma sessão com agente, em qualquer um dos três (sem chave de API — o agente lê o prompt e escreve o JSON):

```bash
cd engine
uv run reel-studio extract aula.mp4
uv run reel-studio transcribe aula.mp4

uv run reel-studio prompt-suggest aula.mp4 --max 5    # modo corte: mostra o prompt
# o agente escreve cortes.json a partir do prompt
uv run reel-studio save-clips aula.mp4 --file cortes.json --max 5
uv run reel-studio cut aula.mp4 --theme busize

uv run reel-studio prompt-script aula.mp4 --style isometric-pastel   # modo VSL
# o agente escreve roteiro.json a partir do prompt
uv run reel-studio save-scenes aula.mp4 --style isometric-pastel --theme forge --file roteiro.json
uv run reel-studio render aula.mp4 --theme forge
```

Fora do Claude Code, para automação (CI, cron), use `suggest` e `script` no lugar de `prompt-suggest`/`save-clips` e `prompt-script`/`save-scenes`: eles chamam o OpenRouter direto, com `OPENROUTER_API_KEY` no `.env`.

## Temas e estilos

Tema é a sua marca (cores, fontes, legenda, CTA): qualquer pessoa cria o dela. `pessoal`, `busize` e `forge` são as minhas, incluídas como exemplo real; `exemplo` é o template genérico para copiar (veja a skill, referência "criar tema").

**Estilos disponíveis**, copiados do [AI Style Atlas](https://www.futurepedia.io/resources/ai-style-atlas/view) para não depender do site:

| Estilo | Bom para |
|---|---|
| Flat Vector Science | Conceitos e metáforas |
| Whiteboard Explainer | Raciocínio passo a passo |
| Isometric Pastel | Processos e fluxos |
| Manim Style Math | Números e fórmulas (render na fase 3) |

## Segurança e privacidade

- Vídeo e áudio **nunca** saem da sua máquina.
- Dentro do Claude Code, nem a transcrição sai: o próprio Claude lê o prompt e gera o JSON, sem chamada de rede nova.
- No caminho de automação (fora do Claude Code), só a transcrição compactada vai ao provedor que você escolher no OpenRouter.
- A chave de API, quando usada, fica em `.env`, fora do controle de versão.
- O Remotion tem licença gratuita para uso pessoal e empresas de até 3 pessoas; acima disso, [confira a licença](https://www.remotion.dev/license) antes de usar em produção.

## Versões

| Versão | Novidades |
|---|---|
| **0.1.0** | Primeira versão: modo corte completo, modo VSL com 3 estilos SVG, 3 temas + exemplo, plugin do Claude Code. |

## Licença

[MIT](LICENSE)
