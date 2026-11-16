# Plano — 03 Enquadramento automático do corte

| Onda | Task | Depende de | Paralelo | Rules/IDs |
|---|---|---|---|---|
| 1 | feat-03-01 layout automático (`fill`, `zoom`, `fit`) com `core/frames.py` e `cut` | — | não | SEG-01, SEG-03, SEG-07, ARQ-04, ARQ-05, ARQ-10, DUP-03, TST-01 |
| 2 | feat-03-02 fundo do tema, faixa do conteúdo e zoom no tempo | 01 | não | SEG-03, ARQ-05, ARQ-10, DUP-03, TST-01 |
| 2 | feat-03-03 glossário de correções da transcrição | — | sim | SEG-01, SEG-02, ARQ-05, ARQ-06, ARQ-10, DUP-01, TST-01 |
| 3 | feat-03-04 folga de fala e fade nos cortes | 02 | não | SEG-01, SEG-03, ARQ-05, ARQ-06, ARQ-10, DUP-01, TST-01 |
| 4 | feat-03-05 fixar `av<17` no extra `transcribe` | — | sim | ARQ-04, SEG-07, TST-01 |
| 4 | feat-03-06 `--file`/`--style` em `save-clips` e `save-scenes` | — | sim | ARQ-06, SEG-01, TST-01 |
| 4 | feat-03-07 preflight do filtro `ass` no `cut` | — | sim | SEG-03, ARQ-05, DUP-03, TST-01 |
| 5 | feat-03-08 modelo maior e `initial_prompt` | 05, 03 | não | SEG-01, ARQ-05, ARQ-10, DUP-01, TST-01 |
| 5 | feat-03-09 variantes regionais no glossário | 03 | sim | SEG-01, ARQ-06, DUP-01, TST-01 |
| 6 | feat-03-10 região por densidade, na proporção da faixa | 02 | não | SEG-03, ARQ-05, ARQ-10, DUP-03, TST-01 |
