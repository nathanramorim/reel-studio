# feat-07-02-motor-multiplataforma — Requisitos pelo motor multiplataforma (Linux, Windows e macOS)

**Pedido:** o prompt e o script da feat-07-01 são centrados no Mac (Homebrew e `curl … | sh`, que só roda em POSIX). Migrar para o motor `requisitos-para-ia` (receita declarativa por sistema), sem Homebrew como pré-requisito, com CI nos três sistemas.
**Branch:** `feat/07-prompt-instalacao` (mesmo PR #8, sem merge).

## Modelo do módulo
`enxuto`: o motor é vendorizado (cópia exata, `skills.lock` com origem, commit e sha256) e o repositório escreve só o `requisitos.toml` na raiz. Origem: `nathanramorim/requisitos-para-ia`, branch `feat/0001-motor-multiplataforma`, commit `5f63e02` (contrato `sdd/spec/contrato-requisitos.md`). Arquivos: `scripts/requisitos.py`, `scripts/bootstrap.sh`, `scripts/bootstrap.ps1`. O motor não tem pasta de trabalho por comando: os comandos usam `uv sync --project {raiz}/engine` e `npm --prefix {raiz}/render`; o Chrome do Remotion é baixado por um script `browser` do `render/package.json` (o `npm run` roda dentro de `render/`, onde o render procura).

## Decisões do projeto aplicadas
`ARQ-12` e ADR-0006 (o prompt usa o script); `SEG-04` e `SEG-05` (a chave do OpenRouter é `credencial`: o motor só confere se a variável existe e nunca mostra o valor); Regra 6 (`uv`, nunca `pip`); `SEG-03` (comandos como lista, sem shell); licença do Remotion é tipo `pessoa`.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Script de requisitos | `scripts/requisitos.py` (feat-07-01) | script próprio, só macOS com brew e Windows com winget | substituir | O motor cobre os três sistemas com receita declarativa e trava contra agir pela pessoa. |
| Itens | feat-07-01 | uv, python, ffmpeg, libass, 3 extras, modelos Whisper e htdemucs, Node, npm, Chrome, licença Remotion, OpenRouter | reusar | Mesmos itens, agora por sistema. |
| Versões travadas | `engine/uv.lock`, `render/package-lock.json` | torch 2.2.2, onnxruntime 1.32.0, Remotion 4.0.543 | respeitar | Python 3.11 ou 3.12 (3.13+ não instala o lock); Mac Intel sem wheel do onnxruntime; Windows arm64 sem av, torch, OpenCV e Chrome. |
| Dispositivo | `core/transcribe.py`, `core/audio.py` | faster-whisper `device="auto"`; demucs pelo CLI | documentar | CUDA quando houver; CPU nos demais; MPS não é usado. |
| Chrome Headless | `@remotion/renderer` 4.0.543 | baixa em `node_modules/.remotion` a partir da pasta do `package.json` mais próximo do cwd | script `browser` | `npm --prefix render run browser` roda dentro de `render/`. |

## Dependências novas
Nenhuma (motor só com biblioteca padrão; o script `browser` usa o `@remotion/cli` que já existe).

## Rules e IDs da Constituição Aplicáveis
`ARQ-12`, `ARQ-06`, `SEG-01`, `SEG-03`, `SEG-04`, `SEG-05`, `COD-02`, `TST-01`.

## Escopo
- Vendorizar os três arquivos do motor (cópia exata do commit `5f63e02`), `skills.lock` com sha256, `.gitattributes` para manter os bytes no Windows.
- `requisitos.toml` com `repo = "nathanramorim/reel-studio"`: uv; Python 3.11/3.12; ffmpeg, ffprobe e libass (Homebrew `ffmpeg-full` + `brew link`, MacPorts, estático, apt, dnf, pacman, zypper, winget `Gyan.FFmpeg`, scoop, choco); extras `transcribe` (obrigatório), `voice` e `vision` com o que não roda por sistema; compilador e Rust (Linux arm64, sphn); runtime do Visual C++ (Windows); modelos Whisper small (`REEL_WHISPER_MODEL`, caches do Hugging Face) e htdemucs (cache do torch); Node 18+, `npm ci` do render, bibliotecas do Chrome no Linux (Alpine não roda), Chrome Headless Shell; licença do Remotion (até 3 pessoas) e vídeo e tema como `pessoa`; OpenRouter como `credencial` opcional; disco e memória.
- README: bloco "Cole isto na sua IA" igual à saída de `requisitos.py prompt`; caminho com clone e sem clone; tabela sem comandos só do Mac; versão 0.3.0 e tabela de versões.
- Skill de resolução de problemas e dicas do motor (`FFMPEG_HINT`, preflight do corte) sem Homebrew como único caminho; ADR-0006 aponta o motor.
- Testes leves (`engine/tests/test_requisitos.py`) e CI `.github/workflows/requisitos.yml` (ubuntu, windows, macos: `validar`, `checar --json` falhando só se o motor quebrar, bootstrap sem uv e `instalar --dry-run`, testes leves).
- Fora: tirar temas e perfis pessoais (follow-up separado).

## Critérios de Aceitação Executáveis
1. `uv run scripts/requisitos.py validar` sai 0 e `uv run scripts/requisitos.py checar --json` gera JSON válido nesta máquina.
2. `cd engine && uv run pytest -q && uv run ruff check .` passam.
3. `shasum -a 256 scripts/requisitos.py scripts/bootstrap.sh scripts/bootstrap.ps1` bate com o `skills.lock` e com o commit `5f63e02` do motor.
4. O bloco do README é igual à saída de `uv run scripts/requisitos.py prompt`; `grep -c 'brew install uv' README.md` = 0 e `grep -c 'install.sh | sh' README.md` = 0.
5. `uv run verificar_readme.py README.md` (readme-studio mais novo) imprime `requisitos: ok`.
6. CI `requisitos` verde em ubuntu-latest, windows-latest e macos-latest no PR #8.
