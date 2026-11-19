# feat-07-01-prompt-instalacao — Requisitos com script e prompt de instalação para a IA

## Modelo do módulo
enxuto — um script avulso (`scripts/requisitos.py`, só biblioteca padrão), seus testes e o README; não mexe no motor nem nos contratos.

## Decisões do projeto aplicadas
- **ARQ-12 (nova, ADR-0006):** o prompt para a IA usa o script como ferramenta; o que é determinístico (conferir e instalar requisitos) vive no script.
- **Regra 6 / ADR-0004:** Python só via `uv`; o README nunca manda `pip install`; o script tem cabeçalho PEP 723 e roda com `uv run` (inclusive pela URL, antes de clonar).
- **Regra 4 / SEG-04 / SEG-05:** o item `openrouter` só explica; o script não lê, não mostra e não grava `OPENROUTER_API_KEY`.
- **Regra 8 / ARQ-04:** `voice` e `vision` continuam extras opcionais; só `transcribe` é obrigatório.
- **Regra 12:** `## Requisitos` antes de `## Instalação`, com o `verificar_readme.py` do readme-studio passando.
- **SEG-03:** comandos sempre em lista de argumentos, sem shell.
- **Regra 3:** temas e estilos pessoais ficam como estão (fora do escopo; a divergência segue registrada).
- Módulo Plugin (versão 0.2.0) e fluxo de instalação do plugin.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Checagem do ffmpeg com libass | `engine/src/reel_studio/core/cut.preflight`, `core/proc.has_filter`, `proc.under_rosetta` (feat-03-07) | procura o filtro `ass` e monta `arch -arm64 brew install ffmpeg-full` sob Rosetta | espelhar | O script precisa rodar antes do clone e antes do `uv sync`, só com a biblioteca padrão; importar `reel_studio` puxaria `typer`, `httpx` e `jsonschema`. Mesmo critério, citado no código. |
| Modelo do Whisper | `core/transcribe.resolve_model` (`REEL_WHISPER_MODEL`, padrão `small`, lista fechada) | valida o nome do modelo | espelhar | Mesma lista fechada; valor fora dela vira `faltando` (o motor recusaria), sem ir para comando nenhum. |
| Mensagens de extra faltando | `core/transcribe.py`, `core/audio.py` (`uv sync --extra ...`) | dica por extra | estender | O script usa `uv sync --inexact --extra X` para não remover os outros extras. |
| Doctor/diagnóstico | motor | não existe | criar | Primeiro diagnóstico do reel-studio. |

## Dependências novas
Nenhuma. O script usa só a biblioteca padrão do Python.

## Rules e IDs da Constituição Aplicáveis
ARQ-04, ARQ-06, ARQ-12, SEG-03, SEG-04, SEG-05, COD-02, COD-05, TST-01, TST-03, TST-04, FLX-07, GOV-01

## Escopo
- `scripts/requisitos.py checar [--json] [--raiz PASTA]`: um item por requisito com `nome`, `estado` (`ok` | `faltando` | `opcional`), `versao`, `obrigatorio`, `tipo` (`sistema`, `projeto`, `download`, `seu`), `comandos` (listas de argumentos) e `explicacao` em português simples; tabela `Requisito | Estado | Versão | Como resolver` ou JSON `{"ok", "requisitos"}`; código 1 se faltar obrigatório.
- Itens: `uv`, `python` (>= 3.11), `ffmpeg`, `ffmpeg-libass`, `extra-transcribe` (obrigatório), `extra-voice`, `extra-vision`, `whisper-<modelo>`, `demucs-modelo`, `node` (>= 18), `render-npm` (Remotion do `package-lock.json`), `chrome-headless` (`npx remotion browser ensure`), `licenca-remotion` (seu) e `openrouter` (seu).
- Raiz: `--raiz`, `CLAUDE_PLUGIN_ROOT`, a pasta do script, a pasta atual (ou acima) ou o plugin instalado em `~/.claude/plugins/cache/reel-studio/reel-studio/<versão mais nova>`. Sem raiz, os itens do projeto ficam sem comando, com a explicação "depois de instalar o plugin".
- `instalar [--sim] [item ...]`: com nomes, cuida só desses itens (nome desconhecido sai com código 2 e a lista dos válidos); sem nomes, de tudo o que falta. Confere de novo, pula o que está ok (idempotente), mostra o comando de cada item; sem `--sim` pergunta "Rodar agora? [s/N]" antes de cada um (sem terminal, só mostra); `--sim` roda sem perguntar; itens `seu` nunca rodam. Nunca aceita licença (Remotion: grátis até 3 pessoas, só mostra) nem lê chave.
- README: `## Antes de começar` vira `## Requisitos` completa (7 pontos + extras), com o bloco "Cole isto na sua IA antes de instalar" antes da instalação (a IA pergunta antes de instalar o `uv`, pede o ok item a item e roda `instalar --sim <item>` só para o que foi aprovado); tabela de versões com a 0.2.0.
- Versão 0.2.0 em `.claude-plugin/plugin.json`, `engine/pyproject.toml` e `reel_studio.__version__`.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest -q tests/test_requisitos.py`: tudo ok sai sem obrigatório faltando; ffmpeg ausente e sem libass dão `faltando` com `brew install ffmpeg-full` (+ `brew link`); Rosetta põe `arch -arm64`; extras usam `uv sync --inexact` em `engine/`; sem raiz não há comando de projeto; `REEL_WHISPER_MODEL` válido muda o modelo e inválido fica `faltando` com aviso (sem ecoar o valor); a chave do OpenRouter nunca aparece na saída; `instalar` não roda nada sem pendência, nunca roda item `seu`, só mostra sem terminal, pergunta antes de cada item e devolve 1 se um comando falhar; com nome de item cuida só dele, item já ok não roda nada e nome desconhecido sai 2 com a lista dos válidos; `main checar` sai 1 quando falta obrigatório; acha o plugin instalado mais novo.
- `uv run scripts/requisitos.py checar` roda neste Mac e mostra a tabela; `uv run scripts/requisitos.py instalar < /dev/null` não roda nada.
- `uv run <readme-studio>/scripts/verificar_readme.py README.md` imprime `requisitos: ok`; `grep -n "pip install" README.md` não acha nada.
- `cd engine && uv run pytest -q && uv run ruff check . ../scripts/requisitos.py` passam; `forge gate` passa.
