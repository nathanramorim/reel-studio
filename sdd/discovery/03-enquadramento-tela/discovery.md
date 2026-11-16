# Discovery 03 — Enquadramento automático do corte (pessoa e tela)

## Problema
O `cut` enche o quadro 9:16 com corte central. Em gravação de tela de 2860×1776 sobra só ~35% da largura e o conteúdo some (origem: `feat-01-04`).

## Para quem
Quem grava a tela ou a si mesmo, em paisagem ou em pé, e quer reels legíveis sem passar parâmetro.

## Jornada
1. A pessoa pede o corte do vídeo.
2. O motor decide sozinho o enquadramento e informa o layout (`layout: zoom (2860x1776)`).
3. O reel sai 1080×1920 e legível.

## Regras de negócio
- Tudo automático; `--layout` e `--anchor` são só override raro; a skill não pergunta.
- Em pé, ou paisagem com rosto consistente (≥ ~8% da altura): `fill`, centrado no rosto.
- Paisagem sem rosto (tela) com atividade concentrada: `zoom` na região que muda, resto em fundo desfocado, legenda na faixa livre.
- Atividade espalhada, parada ou sem OpenCV: `fit` (tela inteira).
- Detecção sempre local; o LLM nunca vê mídia (ADR-0001).

## Escopo
**Dentro:** escolha automática de layout em `cut`, detecção de rosto e de atividade, extra opcional `vision`.
**Fora:** `focus` manual com `--region`, rastreio de cursor quadro a quadro.

## Riscos
| Risco | Mitigação |
|---|---|
| Webcam pequena num canto lida como pessoa | Limiar de ~8% da altura; calibrar com vídeos reais |
| Atividade mal detectada | Fallback `fit`; override por flag |
| OpenCV pesado | Extra opcional; sem ele, `fit` |
