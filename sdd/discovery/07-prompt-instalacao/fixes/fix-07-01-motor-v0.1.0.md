# Fix 07-01: motor de requisitos fixado na tag v0.1.0

**Relato:** a feat-07-02 vendorizou o motor `requisitos-para-ia` do commit `5f63e02` (branch, sem tag). O motor agora tem a tag `v0.1.0` (commit `93abe08`; código aprovado `13733cf`), com validação mais estrita (contrato `sdd/spec/contrato-requisitos.md`, ADR-0008 do motor). Com a v0.1.0, o `validar` da receita deste repositório sai 2.
**Branch:** `fix/07-01-motor-v0.1.0`, a partir de `origin/main` (PR para `main`, sem empilhar).

## Feature Correlacionada
- **Origem:** `features/feat-07-02-motor-multiplataforma.md` (PR #8, mesclado).
- **Causa-raiz:** o motor não tinha tag quando a 07-02 foi feita (`skills.lock` com `ref` de branch e `commit` `5f63e02`). A v0.1.0 passou a recusar duas formas que a receita usava: especificador de versão com dois operadores e código inline de interpretador.
- **Evidência:** `uv run <motor v0.1.0> --arquivo requisitos.toml validar` sai 2 com três recusas:
  - `python.checar.comando`: metacaractere de shell em `'>=3.11,<3.13'`;
  - `modelo-whisper.receita[0]`: código inline (`python -c "__import__('faster_whisper')..."`);
  - `modelo-demucs.receita[0]`: código inline (`python -c "__import__('demucs.pretrained')..."`).

## Modelo do módulo
`enxuto`: troca de cópia vendorizada e ajuste de três itens da receita. Os três arquivos do motor viram cópia exata dos blobs da tag (`git show v0.1.0:<arquivo>`); o lock ganha `ref`, `commit` e sha256 novos.

## Decisões do projeto aplicadas
`ARQ-04` (sem dependência nova); o prompt continua sendo a saída do motor; testes sem rede; Python só pelo `uv`.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Motor vendorizado | `scripts/requisitos.py`, `bootstrap.sh`, `bootstrap.ps1` | cópia do `5f63e02` | substituir | Cópia exata da `v0.1.0`; `bootstrap.sh` é idêntico. |
| Origem e checksum | `skills.lock` | ref de branch e commit `5f63e02` | estender | `ref: v0.1.0`, `commit: 93abe08`, sha256 novos. |
| Python do motor | `requisitos.toml` (`python`) | `uv python find --system ">=3.11,<3.13"` | corrigir | O `RX_VERSAO` da v0.1.0 aceita um só operador. Todos os `uv sync` da receita usam `--python 3.12`, então o `checar` passa a procurar o `3.12` (regex `3\.12`). `>=3.11` com `versao_maxima` não serve: o `find` pode devolver um 3.13 mesmo havendo 3.12. |
| Pré-download dos modelos | `modelo-whisper`, `modelo-demucs` | `uv run ... python -c ...` | trocar por `manual` | A v0.1.0 recusa código inline (saída de emergência do contrato: `manual`). Os dois itens são opcionais e os modelos já baixam sozinhos no primeiro uso; o engine não tem comando de pré-download. |
| Bloco do README | `requisitos.py prompt` | bloco da feat-07-02 | reusar | Segue literal no README (teste `test_readme...`). |
| Teste do lock | `engine/tests/test_requisitos.py` | confere `commit` `5f63e02` | estender | Passa a conferir `ref` `v0.1.0` e `commit` `93abe08`. |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
`ARQ-04`, `ARQ-06`, `TST-04`, `FLX-07`, `SEG-01`.

## Escopo
- Os três arquivos do motor = blobs da tag `v0.1.0`; `skills.lock` atualizado.
- `requisitos.toml`: cabeçalho, `python` (3.12), `modelo-whisper` e `modelo-demucs` (`manual`).
- README (`Programas`: Python 3.12; linha da 0.3.1), `sdd/releases/history.md`, teste do lock, versão 0.3.1 (plugin, `engine/pyproject.toml`, `__init__.py`, `uv.lock`).

## Critérios de Aceitação Executáveis
1. Para cada arquivo do motor, `git hash-object scripts/<f>` = `git -C ../requisitos-para-ia rev-parse v0.1.0:scripts/<f>`, e o sha256 bate com o `skills.lock`.
2. `uv run scripts/requisitos.py validar` sai 0 com `macos, linux, windows cobertos`.
3. `uv run scripts/requisitos.py checar --json` sai 0 ou 1 com JSON válido; o `python` sai `ok` numa máquina com o 3.12 gerenciado pelo uv.
4. `grep -c 'python", "-c"' requisitos.toml` = 0.
5. `cd engine && uv run --python 3.12 pytest -q tests/test_requisitos.py` passa.
6. CI `requisitos` verde em ubuntu, windows e macos.
