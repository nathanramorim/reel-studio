# Plano — 05 Reels premium

| Onda | Task | Depende de | Paralelo | Rules/IDs |
|---|---|---|---|---|
| 1 | feat-05-01 zona segura da vertical e tempo de leitura (conteúdo novo; a legenda do corte não muda) | — | sim | SEG-01, ARQ-05, DUP-03, TST-01 |
| 1 | feat-05-02 kit da marca no tema (`brand`: logo, mascote, painel, pacote) e ajuste do `forge.json` | — | sim | ARQ-06, DUP-01, TST-01 |
| 1 | feat-05-03 contratos: `overlays` no `clips.json`, entradas conteúdo e livre, `media` nas cenas; padrões de voz e legenda no VSL a partir de vídeo | — | sim | ARQ-06, SEG-01, DUP-01, TST-01 |
| 2 | feat-05-04 corte com componentes: camada transparente (gancho, palavra-chave, passos, moldura de janela, barra de progresso, CTA, logo) composta sobre o corte intacto | 01, 02, 03 | não | SEG-03, ARQ-05, ARQ-10, DUP-03, TST-01 |
| 2 | feat-05-05 estilo `forge-motion` para o VSL: painéis de terminal, pacotes luminosos, texto em degradê, fundo e câmera vivos | 01, 02 | sim | ARQ-06, DUP-01, DUP-03, TST-01 |
| 3 | feat-05-06 texto sincronizado com a fala (palavras com tempo) | 04, 05 | não | ARQ-10, DUP-03, TST-01 |
| 3 | feat-05-07 transições entre cenas (saída e entrada escalonadas; passar pelo fundo) | 05 | sim | DUP-03, TST-01 |
| 3 | feat-05-08 janela com a tela real nas cenas do VSL (recorte automático) e aviso de dado sensível | 03, 05 | sim | SEG-03, SEG-05, DUP-03, TST-01 |
| 4 | feat-05-09 roteiro estilo brag: gancho, destaques, fecho, `--tone`, copy, e as entradas conteúdo e livre | 03 | sim | ARQ-06, SEG-05, TST-01 |
| 4 | feat-05-10 trilha e efeitos na grade de batidas, **ligada por padrão sem áudio** e sempre abaixo da voz (`--music`) | 05 | sim | ARQ-04, ARQ-05, SEG-03, DUP-03, TST-01 |
| 4 | feat-05-11 voz gerada a partir de gravação: amostra automática, clone local (extra `tts`), duração das cenas e tempos de palavra pelo áudio gerado, consentimento e ADR-0003 | 03, 06 | não | ARQ-04, SEG-03, SEG-05, SEG-07, DUP-03, TST-01 |
| 4 | feat-05-12 QA e entrega: quadros do meio da transição, pôster no quadro 0, `share-copy.txt`, créditos do `/brag` | 06, 07, 09, 11 | não | ARQ-05, DUP-03, TST-01 |
| 5 | feat-05-13 ajustes visuais do corte com componentes e do `forge-motion` | 04, 05 | não | ARQ-05, DUP-03, TST-01 |
