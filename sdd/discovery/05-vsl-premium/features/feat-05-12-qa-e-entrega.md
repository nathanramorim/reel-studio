# feat-05-12-qa-e-entrega — QA e entrega: quadros do meio da transição, pôster, `share-copy.txt` e créditos

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Checagem de quadros | `render/scripts/check-render.mjs` | fonte, escala, cobertura, paleta | estender | `--all` junta zona segura, transições, palavras e mídia |
| Saída do render | `core/render.execute`, `core/cut.execute` | mp4 | estender | Pôster no quadro 0 e `share-copy.txt` |
| README | `README.md` | instalação e uso | estender | Créditos do `/brag` e referências |
| Copy | `scenes.json` `share` (`feat-05-09`) | texto para postar | reusar | Fonte do `share-copy.txt` |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
ARQ-05, DUP-03, TST-01

## Escopo
- `check-render.mjs --all` roda as checagens de zona segura, transições, palavras e mídia sobre os quadros tirados da linha do tempo.
- **Pôster:** o quadro parado mais forte (texto inteiro e assentado) vira `poster.jpg` e **substitui** o quadro 0 do mp4, sem mudar a duração nem a sincronia do áudio.
- **`share-copy.txt`:** de 1 a 3 frases, vindas de `share`, prontas para postar.
- Vale para o VSL e para o corte com componentes; sem camadas, o corte sai como hoje (sem pôster forçado).
- README ganha a seção de referências, com os créditos do `/brag` (MIT, `latent-spaces/brag`) e do vídeo do pipeline do Forge.

## Critérios de Aceitação Executáveis
- `cd render && node scripts/check-render.mjs --all` passa.
- `cd engine && uv run pytest tests/test_render.py -k "poster or share"`: o plano troca o quadro 0 sem mudar a duração; `share-copy.txt` sai de `share`; sem `share`, não gera o arquivo.
- `ffprobe -count_frames` do mp4: número de quadros igual a duração × fps, e o quadro 0 igual ao pôster.
- `grep -n "brag" README.md` mostra os créditos.
- `cd engine && uv run pytest && uv run ruff check` passam.
