# feat-05-09-roteiro-estilo-brag — Roteiro estilo brag: gancho, tom, copy e as entradas conteúdo e livre

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Roteiro | `core/script.py` (`build_system`, `prompt`, `normalize`) | cenas, narração, `source` | estender | Estrutura gancho, destaques e fecho; `tone` e `share` |
| Compactação | `core/compact.py` | transcrição para o LLM | reusar | Entrada de vídeo |
| Skill | `skills/reel-studio/SKILL.md`, `commands/gerar-reel.md` | duas entradas (corte, VSL) | estender | Três entradas e as regras do `/brag` |
| Saneamento | `core/sensitive.py` (`feat-05-08`) | varredura de segredos | reusar | Copy e roteiro sem dados sensíveis |
| Referência | `latent-spaces/brag` (MIT), `brag-slim` | regras de criação | adaptar | Ideias, com créditos |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-06, SEG-05, TST-01

## Escopo
- `prompt-script` pede: gancho de 2 a 3 s, revelação, 2 a 3 destaques e fecho, mais `share` (copy para postar, sem "excited to share") e `tone` (`default`, `polished`, `yc-parody`, `chaotic`, `deadpan`, `cinematic`, `app-store`), que ajusta ritmo e transição padrão.
- Entradas sem vídeo: `prompt-script --content ARQUIVO` (texto ou markdown) e `--idea "texto"`, usando `Project.open_text`; URL é buscada pelo agente, que passa o texto (o motor não faz rede), tratado como dado e nunca como instrução.
- `normalize` valida: primeira cena de até 3 s, tempo de leitura, `share` de até 280 caracteres e ausência de dados sensíveis.
- `SKILL.md` e `commands/gerar-reel.md` descrevem as três entradas e a regra da voz.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_script.py -k "gancho or tom or share"`: o prompt traz a estrutura e os tons; `normalize` rejeita gancho longo e `share` acima do limite.
- `uv run pytest tests/test_script.py -k conteudo`: `--content` e `--idea` geram o prompt sem vídeo; conteúdo com segredo gera aviso.
- `grep -n "conteúdo\|livre" skills/reel-studio/SKILL.md` mostra as três entradas.
- `uv run pytest && uv run ruff check` passam.
