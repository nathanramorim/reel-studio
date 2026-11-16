<p align="center">
  <img src="docs/banner.svg" alt="reel-studio: Seus vídeos, virando reels." width="100%">
</p>

<p align="center">
  <a href="https://github.com/nathanramorim/reel-studio/releases"><img alt="versão" src="https://img.shields.io/github/v/tag/nathanramorim/reel-studio?label=vers%C3%A3o&color=4f8ef7&labelColor=0d0f14"></a>
  <img alt="licença" src="https://img.shields.io/badge/licen%C3%A7a-MIT-4f8ef7?labelColor=0d0f14">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-plugin-4f8ef7?labelColor=0d0f14">
  <img alt="uv" src="https://img.shields.io/badge/Python-uv-4f8ef7?labelColor=0d0f14">
  <img alt="dados" src="https://img.shields.io/badge/dados-100%25%20locais-4f8ef7?labelColor=0d0f14">
</p>

<h3 align="center">Corte real ou VSL animado, na sua marca.<br>Tudo local; uma chamada de IA por vídeo.</h3>

---

## O que é

O **reel-studio** transforma um vídeo que você já gravou em um reel vertical para o Instagram. Dois modos: **corte**, que recorta o trecho real do vídeo, e **VSL**, que reescreve a fala como um roteiro curto e anima num dos estilos visuais.

A transcrição roda local (Whisper). O modelo de IA só vê o texto, nunca o vídeo nem o áudio, numa única chamada por etapa. Nada é gerado sem você aprovar o corte ou o roteiro primeiro.

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
- **Claude Code**, para instalar como plugin.
- Chave da sua conta no [OpenRouter](https://openrouter.ai) (`OPENROUTER_API_KEY`), para `suggest` e `script`.

## Instalação

```
/plugin install reel-studio --marketplace nathanramorim/reel-studio
```

Ou, fora do Claude Code:

```bash
claude plugin marketplace add nathanramorim/reel-studio
claude plugin install reel-studio
```

Ou clone e rode direto:

```bash
git clone https://github.com/nathanramorim/reel-studio
cd reel-studio/engine && uv sync --extra transcribe
cd ../render && npm install   # só se for usar o modo VSL
```

## Como usar

No Claude Code, dentro de uma sessão com o plugin instalado:

```
/gerar-reel aula.mp4
```

A skill pergunta o modo, o tema e (no modo VSL) o estilo, mostra o plano e só gera o vídeo depois do seu "sim". Comandos extras: `/transcrever` e `/extrair-voz`.

Pela CLI, direto:

```bash
cd engine
uv run reel-studio extract aula.mp4
uv run reel-studio transcribe aula.mp4
uv run reel-studio suggest aula.mp4 --max 5      # modo corte
uv run reel-studio cut aula.mp4 --theme busize

uv run reel-studio script aula.mp4 --style isometric-pastel --theme forge   # modo VSL
uv run reel-studio render aula.mp4 --theme forge
```

## Temas e estilos

**Temas prontos:** `pessoal`, `busize`, `forge`, e `exemplo` para você copiar e criar o seu (veja a skill, referência "criar tema").

**Estilos disponíveis**, copiados do [AI Style Atlas](https://www.futurepedia.io/resources/ai-style-atlas/view) para não depender do site:

| Estilo | Bom para |
|---|---|
| Flat Vector Science | Conceitos e metáforas |
| Whiteboard Explainer | Raciocínio passo a passo |
| Isometric Pastel | Processos e fluxos |
| Manim Style Math | Números e fórmulas (render na fase 3) |

## Segurança e privacidade

- Vídeo e áudio **nunca** saem da sua máquina.
- Só a transcrição, compactada, é enviada ao provedor de IA que você escolher (via OpenRouter).
- A chave de API fica em `.env`, fora do controle de versão.
- O Remotion tem licença gratuita para uso pessoal e empresas de até 3 pessoas; acima disso, [confira a licença](https://www.remotion.dev/license) antes de usar em produção.

## Versões

| Versão | Novidades |
|---|---|
| **0.1.0** | Primeira versão: modo corte completo, modo VSL com 3 estilos SVG, 3 temas + exemplo, plugin do Claude Code. |

## Licença

[MIT](LICENSE)
