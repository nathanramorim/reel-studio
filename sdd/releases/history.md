# Release Notes — reel-studio

Este arquivo registra o histórico de entregas de produto deste projeto.

## Entregas

### 03 — Enquadramento automático do corte (2026-11-16)
- **Layout automático:** `cut` escolhe sozinho `fill` (pessoa), `zoom` (tela com atividade) ou `fit`, sem parâmetro. Extra opcional `vision` (OpenCV) para detectar rosto e atividade; sem ele, `fit`.
- **Zoom no tempo:** a região acompanha a ação dentro do corte; fundo na cor do tema e legenda `lower-third` abaixo do conteúdo.
- **Glossário:** `correcoes.json` corrige termos errados da transcrição (frases de tamanhos diferentes) antes da legenda e do prompt.
- **Folga e fade:** 0,40 s antes e 0,70 s depois da fala, com fade de vídeo e áudio.
- **Pendente:** validação com gravações reais (C5); calibrar limiares de rosto, histerese, folga e fade.
