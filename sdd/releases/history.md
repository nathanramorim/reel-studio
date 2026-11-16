# Release Notes — reel-studio

Este arquivo registra o histórico de entregas de produto deste projeto.

## Entregas

### 03 — Enquadramento automático do corte (2026-11-16)
- **Layout automático:** `cut` escolhe sozinho `fill` (pessoa), `zoom` (tela com atividade) ou `fit`, sem parâmetro. Extra opcional `vision` (OpenCV) para detectar rosto e atividade; sem ele, `fit`.
- **Zoom no tempo:** a região acompanha a ação dentro do corte; fundo na cor do tema e legenda `lower-third` abaixo do conteúdo.
- **Glossário:** `correcoes.json` corrige termos errados da transcrição (frases de tamanhos diferentes) antes da legenda e do prompt.
- **Folga e fade:** 0,40 s antes e 0,70 s depois da fala, com fade de vídeo e áudio.
- **Região por densidade:** o zoom tem a proporção da faixa do conteúdo (1080×920) e escolhe o tamanho pela cobertura da atividade.
- **Cobertura da transcrição e do corte:** `av<17` fixado, `--file`/`--style` aceitos, aviso se faltar o filtro `ass`, modelo `medium`/`large-v3`, `initial_prompt` e variantes regionais no glossário.
- **Limitações conhecidas (C5):** cortes sobre a tela toda ficam em `fit` (aceito quando a fala é sobre ela; o critério é atividade, não fala); a região não troca no tempo; o Dock pode aparecer. Calibrar limiares de rosto, histerese, folga e fade com mais vídeos.
