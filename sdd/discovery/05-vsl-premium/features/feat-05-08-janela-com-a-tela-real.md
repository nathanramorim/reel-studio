# feat-05-08-janela-com-a-tela-real — Janela com a tela real nas cenas do VSL

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; LLM gera JSON, nunca código de animação; `SceneRenderer` único mapa `type -> componente`; CLI na borda, domínio em `core/`). Iniciativa 04: cores só do tema, estilo só anima.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Recorte da tela | `core/frames.py` (`analyze`, região por densidade) | região de atividade | reusar sem alterar | Define o recorte da janela |
| Janela | `render/src/forge/Pane` (`feat-05-05`) | moldura de terminal | reusar | Contém o vídeo real |
| Áudio original | `core/render.py` (`--audio original`, `source`) | voz por cena | reusar | A voz vem do trecho |
| Dados sensíveis | — | — | criar | `core/sensitive.py`: padrões de segredo, token e e-mail |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-03, SEG-05, DUP-03, TST-01

## Escopo
- Cena com `media: {source}` mostra o trecho real da gravação numa `Pane`, com o recorte automático da região de atividade; o vídeo é servido ao Remotion pelo `--public-dir` da pasta do vídeo (sem rede).
- `core/sensitive.py` varre a transcrição e os textos da cena por segredos, tokens e e-mails e emite aviso; ao usar `media`, sempre avisa que a gravação pode mostrar dados sensíveis e pede conferência.
- A voz, quando original, continua vindo do `source` da cena.

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_render.py -k media`: o plano referencia o vídeo pelo `--public-dir`; cena sem `media` não muda.
- `uv run pytest tests/test_sensitive.py`: detecta chaves, tokens e e-mails; texto limpo não gera aviso; nada sensível é logado (`SEG-05`).
- `cd render && node scripts/check-render.mjs --style forge-motion --media`: o still da cena com `media` mostra a tela dentro da janela, dentro da zona segura.
- `cd render && npx tsc --noEmit`, `uv run pytest && uv run ruff check` passam.
