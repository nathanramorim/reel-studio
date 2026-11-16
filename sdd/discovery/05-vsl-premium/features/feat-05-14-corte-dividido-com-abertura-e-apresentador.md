# feat-05-14-corte-dividido-com-abertura-e-apresentador — Corte dividido, abertura animada e apresentador

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (estilo e tema independentes; CLI na borda, domínio em `core/`; o LLM gera JSON, nunca código de animação). Iniciativa 05: o corte sem a opção nova não pode regredir (C8). Tudo é opt-in: sem `split`, `intro` e `presenter`, o comando do `ffmpeg`, o `.ass` e a saída ficam idênticos aos de hoje.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Geometria do vídeo no quadro | `core/cut.py` (`BAND_Y`, `BAND_H`, `video_filter`, `video_rect`) | `fill`, `zoom` e `fit` numa faixa 1080×920 em y 320 | estender | Novo `layout` `split` com faixa própria; `video_rect` segue sendo o dono do retângulo (DUP-01) |
| Camada de componentes | `core/overlay.py`, `render/src/overlay/Overlay.tsx`, `regions.ts` | gancho, chips, CTA, logo, barra, moldura rente ao vídeo | estender | No `split` as faixas passam a viver abaixo do vídeo; nada de componente cobre a gravação |
| Legenda | `core/captions.py` (`MARGIN_V`, `lower-third`) | legenda em y 1180 a 1360 | reusar sem alterar | A legenda não muda de lugar |
| Mascote e logo | `brand.mascot` (`themes/forge.json`), `overlay.with_assets` | SVG do tema vira data URI | reusar | O apresentador é o mascote do tema, sem arte nova |
| Tempo das palavras | `feat-05-06`, `transcript.json` | palavras com início e fim | reusar | O apresentador reage à fala |
| Cena e fundo vivo do `forge-motion` | `render/src/forge/LiveBackground.tsx`, `Camera.tsx` | fundo, câmera e degradê | reusar | A abertura usa a mesma linguagem do VSL |
| Composição de vídeos | `core/overlay.py` (`compose_args`), `core/deliver.py` | `ffmpeg overlay` e entrega | estender | Novo passo de concatenação da abertura antes do corte |

## Dependências novas
Nenhuma. O Remotion e o `ffmpeg` já são usados; a abertura é uma composição nova do mesmo projeto.

## Rules e IDs da Constituição Aplicáveis
SEG-03, ARQ-05, ARQ-06, ARQ-10, DUP-01, DUP-03, TST-01

## Suposições (a confirmar pelo humano; mudam só números e nomes)
1. **Divisão da tela:** o vídeo fica na parte de cima, em y 250 a 950 (700 px, `fit`; uma gravação 16:10 ocupa 1080×675). A parte de baixo (y 970 a 1536) leva a legenda, o comentário e as instruções.
2. **Apresentador:** o mascote do tema (`brand.mascot`), no rodapé à esquerda, y 1380 a 1530, com um leve movimento enquanto há fala (pulso nas palavras). Sem arte nova; sem `mascot` no tema, não aparece.
3. **Abertura:** 1,5 s antes do corte, com fundo vivo do `forge-motion`, o logo e o gancho do corte em degradê. Silenciosa (sem voz), com a trilha só se `--music` estiver ligada.
4. **Gancho e chips no `split`:** ficam na faixa abaixo do vídeo (y 970 a 1170), com no máximo 2 itens ao mesmo tempo (gancho e um chip); o campo `pos` dos chips passa a ser ignorado no `split`.
5. **Ativação:** `--layout split` na CLI, ou `"layout": "split"` no clipe do `clips.json`. `"intro": {"dur": 1.5}` e `"presenter": true` no clipe. Tudo ausente significa o comportamento de hoje.

## Escopo
1. **Layout `split`** (`core/cut.py`): o vídeo em `fit` na faixa y 250 a 950, fundo do tema nas demais áreas. `video_rect` devolve o retângulo do `split`; a moldura da camada acompanha, como na 05-13.
2. **Faixas abaixo do vídeo** (`regions.ts`, `Overlay.tsx`): no `split`, gancho e chips ocupam y 970 a 1170 (2 slots de 110 px, sem passar da legenda); CTA, barra e logo no rodapé (y 1380 a 1536). Nenhum texto cobre a gravação nem a legenda.
3. **Apresentador:** o mascote no rodapé à esquerda, dentro da zona segura e fora dos 140 px da direita; movimento guiado pelas palavras com tempo (sem tempos, parado).
4. **Abertura animada** (`core/overlay.py` e nova composição `Intro`): vídeo de 1,5 s (padrão) com áudio mudo, gerado pelo Remotion e concatenado antes do corte pelo `ffmpeg`. O corte e a camada continuam idênticos; os tempos dos overlays e da legenda não se deslocam (a abertura é concatenada depois de o corte estar pronto). O intermediário é apagado.
5. **Contrato** (`contracts/clips.schema.json`): `layout` (`fill`, `zoom`, `fit`, `split`), `intro` (objeto com `dur` de 0,5 a 3 e `text` opcional até 60 caracteres) e `presenter` (booleano). Valores fora disso são rejeitados.
6. **Segurança do plano:** `cut --dry-run` mostra o plano (corte, camada, abertura) sem escrever nada (ARQ-05); caminhos e comandos por lista de argumentos (SEG-03).

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest -k regressao`: sem `split`, `intro` e `presenter`, o comando do `ffmpeg` e o `.ass` são idênticos aos de hoje.
- `uv run pytest -k split`: `video_rect` e `video_filter` do `split` (retângulo na faixa y 250 a 950, largura máxima 1080, fundo do tema); `fill`, `fit` e `zoom` não mudam; o contrato aceita e rejeita os valores de `layout`, `intro` e `presenter`.
- `uv run pytest -k intro`: o plano tem um passo de concatenação a mais, a duração final é a do corte mais a abertura, o intermediário é removido e `--dry-run` não escreve nada.
- `cd render && node scripts/check-render.mjs --split`: no `split`, todo texto fica abaixo do vídeo (y >= 970) e acima do rodapé, sem cobrir a legenda (y 1180 a 1360), sem sobreposição entre faixas, com o apresentador na zona segura e a moldura rente ao vídeo.
- `cd render && node scripts/check-render.mjs --all`, `npx tsc --noEmit` e `cd engine && uv run pytest && uv run ruff check` passam.
- Manual (C13): clip-02 e clip-05 da gravação 14.33.02 em `split`, com abertura e apresentador, e comparados com o C9.
