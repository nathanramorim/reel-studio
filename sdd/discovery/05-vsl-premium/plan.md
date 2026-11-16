# Plano — 05 VSL premium

| Onda | Task | Depende de | Paralelo | Rules/IDs |
|---|---|---|---|---|
| 1 | feat-05-01 zona segura da vertical e tempo de leitura (legenda e conteúdo; validação no `normalize`) | — | sim | SEG-01, ARQ-05, DUP-03, TST-01 |
| 1 | feat-05-02 kit da marca no tema (`brand`: logo, mascote, painel, pacote) e ajuste do `forge.json` | — | sim | ARQ-06, DUP-01, TST-01 |
| 2 | feat-05-03 estilo `forge-motion`: painéis de terminal, pacotes luminosos, texto em degradê, fundo e câmera vivos | 01, 02 | não | ARQ-06, DUP-01, DUP-03, TST-01 |
| 2 | feat-05-04 texto sincronizado com a narração (palavras com tempo) | 03 | não | ARQ-10, DUP-03, TST-01 |
| 2 | feat-05-05 transições entre cenas (saída e entrada escalonadas; passar pelo fundo) | 03 | sim | DUP-03, TST-01 |
| 3 | feat-05-06 roteiro estilo brag: gancho, destaques, fecho, `--tone` e copy | 01 | sim | ARQ-06, SEG-05, TST-01 |
| 3 | feat-05-07 trilha e efeitos na grade de batidas (`--music`), com ducking sobre o áudio original | 05 | sim | ARQ-04, ARQ-05, SEG-03, DUP-03, TST-01 |
| 4 | feat-05-08 painel com o trecho real da gravação ("mostrar a coisa") e aviso de dado sensível | 03, 06 | não | SEG-03, SEG-05, DUP-03, TST-01 |
| 4 | feat-05-09 QA e entrega: quadros do meio da transição, pôster no quadro 0, `share-copy.txt`, créditos do `/brag` | 05, 06 | não | ARQ-05, DUP-03, TST-01 |
