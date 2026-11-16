# Critérios — 01 reel-studio MVP

## Modelo do módulo
`completo` para o motor (domínio com contratos e testes); `enxuto` para o plugin (só markdown e manifesto).

## Decisões do projeto aplicadas
ADR-0001 (todas as decisões). Constitution: `ARQ-01`, `ARQ-04`, `ARQ-05`, `ARQ-06`, `SEG-03`, `SEG-04`, `SEG-05`, `DUP-01`, `DUP-04`, `TST-01`.

## Restrições
- `SEG-03`: ffmpeg é chamado com lista de argumentos, nunca com shell.
- `SEG-04` e `SEG-05`: chave do OpenRouter só por env; nunca em log.
- `ARQ-05`: `--dry-run` em `cut` e `render` só imprime o plano.
- `ARQ-04`: transcrição, voz e Manim são extras opcionais do uv.
- `DUP-04`: schemas só em `contracts/`.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Corte com IA | Opus Clip, Descript | SaaS | criar | Dados em nuvem de terceiro |
| Tokens de marca | diagram-studio, readme-studio | JSON de cores | reusar formato | Mesmo autor, mesmas cores |
| Estilos | Futurepedia AI Style Atlas | Descrições e prompts | reusar como referência | Cópia local em `styles/` |
| Plugin | diagram-studio | Estrutura de plugin | reusar | Padrão já validado |

## Dependências novas
`typer`, `httpx`, `jsonschema` (base). Extras: `faster-whisper`, `demucs`, `manim`. Render: `remotion`, `@remotion/cli`, `react`.

## C4: sequência
Ver `sdd/spec/flows.md`.

## Critérios de aceitação executáveis
| # | Critério | Comando |
|---|---|---|
| C1 | Testes do motor passam | `cd engine && uv run pytest` |
| C2 | Lint passa | `cd engine && uv run ruff check` |
| C3 | Temas e estilos validam no schema | `cd engine && uv run reel-studio validate` |
| C4 | Render compila | `cd render && npx tsc --noEmit` |
| C5 | Manifesto do plugin válido | `claude plugin validate .` |
| C6 | Corte real gera mp4 9:16 | `uv run reel-studio cut exemplo.mp4 --theme busize` |
