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

## Requisitos

> **Cole isto na sua IA antes de instalar:**
>
> "Confira os requisitos do reel-studio. Se o repositório ainda não estiver clonado, clone com o GitHub CLI: `gh repo clone nathanramorim/reel-studio` (instale o gh com `winget install --id GitHub.cli -e` no Windows, pelo https://cli.github.com no macOS e pelo pacote `gh` da sua distro no Linux; o `gh auth login` é comigo). No Windows, rode `powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1`; no macOS ou Linux, rode `sh scripts/bootstrap.sh`. Ele confere e, com o meu ok, instala o uv, e depois mostra o que falta. Para cada item, peça meu ok e rode `uv run scripts/requisitos.py instalar --sim <item>`. Itens marcados como é com você (licença, consentimento ou voz, login, permissões do sistema, senha de administrador): me explique e espere eu fazer. Não aceite licenças nem declarações por mim e não mexa em senhas, chaves ou tokens."

O bloco serve para Linux, Windows e macOS. Os requisitos ficam declarados em [`requisitos.toml`](requisitos.toml), com uma receita por sistema, e quem confere é o motor [`requisitos-para-ia`](https://github.com/nathanramorim/requisitos-para-ia), copiado em `scripts/` (origem e commit no [`skills.lock`](skills.lock)). O Homebrew, o MacPorts, o winget e o apt são usados quando existem, mas nenhum deles é pré-requisito: sem eles, o item diz o caminho manual.

- **Com o repositório clonado** (o caminho do bloco acima; sem o GitHub CLI, `git clone https://github.com/nathanramorim/reel-studio` também serve, porque o repositório é público): o bootstrap confere o uv e roda `uv run scripts/requisitos.py checar`. Depois: `uv run scripts/requisitos.py checar --json`, `uv run scripts/requisitos.py instalar --dry-run` (só mostra o plano), `uv run scripts/requisitos.py instalar <item>` (pergunta antes de cada um) e `uv run scripts/requisitos.py plataforma`.
- **Sem clonar** (com o uv já instalado; vale depois do merge na `main`): `uv run https://raw.githubusercontent.com/nathanramorim/reel-studio/main/scripts/requisitos.py --arquivo https://raw.githubusercontent.com/nathanramorim/reel-studio/main/requisitos.toml checar`. Os itens do motor e do render (extras, modelos, `npm ci`, Chrome) só ficam ok dentro do clone.

O motor nunca usa `sudo` sozinho (comandos de administrador ele só mostra), nunca aceita a licença do Remotion e nunca lê nem mostra a chave do OpenRouter: isso é sempre com você.

| Ponto | O que precisa |
|---|---|
| **Onde roda** | Feito e testado no **macOS 14+ com Apple Silicon**. Linux (x64 e arm64) e Windows x64 têm receita, conferida na CI nos três sistemas, mas o vídeo não foi testado neles. **Não roda:** Mac Intel (o `onnxruntime` travado no `uv.lock`, usado pela transcrição, não tem wheel para macOS x86_64; o extra `voice` também não instala lá) e Windows arm64 (sem `av`, PyTorch, OpenCV nem o Chrome do Remotion): use o WSL (Ubuntu) ou uma máquina x64. No Apple Silicon, use o terminal nativo (arm64), não o Rosetta. Agentes: Claude Code (plugin), agy (Antigravity) e Codex (lêem a mesma skill); sem agente, a CLI funciona com o OpenRouter (veja "Contas e chaves"). |
| **Programas** | [`uv`](https://docs.astral.sh/uv/), que o bootstrap instala pelo instalador oficial com o seu ok; ele instala o **Python 3.11 ou 3.12** (o `uv.lock` não instala no 3.13 ou mais novo; você não usa `pip`). **ffmpeg com libass** (a legenda usa o filtro `ass`): no Mac com Homebrew, o `ffmpeg-full` (keg-only, por isso o `brew link`); no MacPorts, no Linux (Ubuntu, Debian, Fedora, Arch, openSUSE) e no Windows (`Gyan.FFmpeg` pelo winget, scoop ou choco), o ffmpeg do pacote já tem libass. **Node.js 18 ou mais novo**, só para o modo VSL e os componentes do corte. O comando de cada sistema sai no `checar`. |
| **Extras do motor** (em `engine/`) | `transcribe` (faster-whisper, **obrigatório**), `voice` (demucs + PyTorch, só para isolar a voz com `--voice-only`) e `vision` (OpenCV, só para o enquadramento automático do corte; sem ele o corte usa `fit`). O motor instala cada um com `uv sync --project engine --python 3.12 --inexact --extra <nome>` (o `--inexact` mantém os outros). |
| **Por sistema** | **Linux:** as bibliotecas do Chrome Headless Shell (lista do Remotion: `libnss3`, `libgbm`, `libasound2t64` ou `libasound2` e outras; Alpine não roda); no arm64, o extra `voice` compila o `sphn` (precisa do `gcc` e do Rust). **Windows:** o runtime do Visual C++ (PyTorch e ctranslate2). **macOS:** o Chrome e as bibliotecas de áudio já vêm prontos. |
| **GPU** | A transcrição usa `device="auto"`: CUDA quando houver as bibliotecas da NVIDIA, senão CPU; o demucs usa CUDA se houver. No Linux x64 o PyTorch do PyPI já traz as bibliotecas CUDA (cerca de 3 GB); no Windows e no macOS é CPU (MPS não é usado). |
| **Downloads na primeira execução** | Modelo do **Whisper** `small` (cerca de 480 MB; outro com `REEL_WHISPER_MODEL=tiny`, `base`, `medium` ou `large-v3`) em `~/.cache/huggingface/hub/` em todos os sistemas (ou `HF_HOME`/`HF_HUB_CACHE`), baixado na primeira transcrição ou adiantado com `instalar modelo-whisper`. Extra `voice`: PyTorch (cerca de 1 GB) no `.venv` e o modelo **htdemucs** (cerca de 80 MB), que o demucs 4.1 baixa do Hugging Face para `~/.cache/huggingface/hub/` (ou `HF_HOME`/`HF_HUB_CACHE`). Modo VSL: `npm ci` em `render/` (Remotion travado em 4.0.543 no `package-lock.json`) e o **Chrome Headless Shell** (cerca de 200 MB) em `render/node_modules/.remotion/`, baixado no primeiro render ou adiantado com `instalar chrome-headless` (roda `npm --prefix render run browser`). Depois disso tudo roda sem internet. |
| **Contas e chaves** | Nenhuma dentro do Claude Code, agy ou Codex: o próprio agente escreve os cortes e o roteiro. **Opcional:** para automação sem agente (`suggest` e `script`), uma chave do OpenRouter em `OPENROUTER_API_KEY`, definida por você no ambiente ou no `.env` (copie de `.env.example`; o `.env` fica fora do git). O motor de requisitos só confere se a variável existe no ambiente; nunca lê o valor nem grava a chave. |
| **Máquina** | RAM: estimativa de 8 GB (não medido; a transcrição e o render rodam no seu computador). Reserve cerca de 3 GB de disco (5 GB no Linux x64) com os extras e o modo VSL, mais o espaço dos vídeos. |
| **Licenças e limites** | Código MIT. faster-whisper e demucs: MIT. OpenCV: Apache 2.0. O **Remotion** é grátis para uso pessoal e para empresas de até 3 pessoas; acima disso, a empresa precisa da [licença paga](https://www.remotion.dev/license). Quem aceita é você: o motor só mostra. |
| **O que você fornece** | O **vídeo** já gravado (ou o áudio, no modo VSL) e o **tema** com a sua marca (cores, fonte, legenda e CTA): copie `themes/exemplo.json` (veja a skill, referência "criar tema"). Você aprova os cortes ou o roteiro antes de qualquer vídeo ser gerado. |

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
cd engine && uv sync --python 3.12 --extra transcribe
cd ../render && npm ci   # só se for usar o modo VSL
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
uv run reel-studio transcribe aula.mp4   # --model medium ou large-v3 acerta mais o sotaque

uv run reel-studio prompt-suggest aula.mp4 --max 5    # modo corte: mostra o prompt
# o agente escreve cortes.json a partir do prompt
uv run reel-studio save-clips aula.mp4 --file cortes.json --max 5
uv run reel-studio cut aula.mp4 --theme busize
# com `overlays` no clips.json, o corte ganha uma camada de componentes (gancho, passos, CTA, logo);
# o mp4 do corte fica intacto e o resultado sai em clip-NN-TEMA-overlay.mp4. --overlays none ignora.

uv run reel-studio prompt-script aula.mp4 --style isometric-pastel   # modo VSL
# o agente escreve roteiro.json a partir do prompt
uv run reel-studio save-scenes aula.mp4 --style isometric-pastel --theme forge --file roteiro.json
uv run reel-studio render aula.mp4 --theme forge --style forge-motion   # --captions narration|none, --audio original|none
```

**`correcoes.json`** (opcional, ao lado do vídeo ou em `--glossary`): mapa `errado -> certo` aplicado à transcrição em memória. Uma chave aceita variantes separadas por `|` (`"checaja|checage|checajem": "checagem"`); a mesma variante com dois valores é erro. O tema pode ter `vocabulary` (lista de termos), que junto aos valores do glossário alimenta o prompt do Whisper (`transcribe --theme TEMA`, `--prompt` para texto extra). `save-clips` e `save-scenes` aceitam `--file` e `--style` ou os mesmos valores como argumentos posicionais.

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
| **0.3.0** | Requisitos em Linux, Windows e macOS pelo motor [`requisitos-para-ia`](https://github.com/nathanramorim/requisitos-para-ia) (cópia em `scripts/`, origem no `skills.lock`): receita por sistema em `requisitos.toml` (o que não roda é dito, com alternativa), bootstrap do uv para cada sistema (`scripts/bootstrap.sh` e `scripts/bootstrap.ps1`), sem Homebrew como pré-requisito, prompt para a IA gerado pelo motor e CI nos três sistemas. |
| **0.2.0** (não publicada como tag) | `scripts/requisitos.py` com `checar` e `instalar` (pergunta antes de instalar e nunca aceita licença por você), seção Requisitos completa e o prompt para colar na IA antes de instalar. Inclui as entregas 03 a 05 da `main` (veja `sdd/releases/history.md`). |
| **0.1.0** | Primeira versão: modo corte completo, modo VSL com 3 estilos SVG, 3 temas + exemplo, plugin do Claude Code. |

## Licença

[MIT](LICENSE)
