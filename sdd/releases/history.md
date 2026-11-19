# Release Notes — reel-studio

Este arquivo registra o histórico de entregas de produto deste projeto.

## Entregas

### 07 — Requisitos em Linux, Windows e macOS pelo motor multiplataforma (0.3.0, 2026-11-19, task feat-07-02)
- **Motor vendorizado:** `scripts/requisitos.py`, `scripts/bootstrap.sh` e `scripts/bootstrap.ps1` copiados de `nathanramorim/requisitos-para-ia@5f63e02` (origem e sha256 no `skills.lock`); o script próprio da 0.2.0 saiu.
- **`requisitos.toml`:** receita por sistema (ffmpeg com libass, extras com Python 3.11/3.12, Node, `npm ci`, Chrome do Remotion e as bibliotecas dele no Linux, caches dos modelos); Mac Intel e Windows arm64 marcados como não suportados, com alternativa; sem Homebrew como pré-requisito; licença do Remotion e chave do OpenRouter continuam com a pessoa.
- **README:** o bloco para a IA é a saída de `requisitos.py prompt`; caminho com clone e sem clone. **CI:** `.github/workflows/requisitos.yml` em ubuntu, windows e macos.
- **render:** script `browser` (`remotion browser ensure`) para baixar o Chrome dentro de `render/`.

### 07 — Prompt de instalação para a IA (0.2.0, 2026-11-19) (não publicada como tag)
- **`scripts/requisitos.py`:** `checar` mostra cada requisito (ok, faltando ou opcional, versão e comando); `instalar` pergunta antes de cada comando, pula o que já está ok e nunca aceita licença nem lê chave. Roda antes de clonar, pela URL.
- **README:** seção `## Requisitos` completa e o bloco "Cole isto na sua IA antes de instalar".
- **Constitution:** `ARQ-12` (ADR-0006): o prompt para a IA usa script como ferramenta.

### 05 — Reels premium, ondas 1 e 2 (2026-11-16, PRs #4 e #6)
- **Zona segura e tempo de leitura (05-01):** o texto das cenas fica dentro da área segura da vertical; cena curta demais para ler é recusada.
- **Kit da marca no tema (05-02):** campo `brand` no tema.
- **Contratos de overlays (05-03):** `overlays`, entradas de conteúdo e livres e `media` nos contratos.
- **Corte com componentes (05-04):** camada de componentes (gancho, passos, CTA, logo) sobre o corte, que fica intacto (`clip-NN-TEMA-overlay.mp4`).
- **Estilo `forge-motion` (05-05):** painéis, pacotes, degradê, fundo e câmera vivos.
- As ondas seguintes (05-06 a 05-12) ainda não foram entregues.

### 04 — VSL: áudio e estilo visual (2026-11-16, PR #3)
- **Fontes e escala (04-01):** fontes locais e escala tipográfica para 1080×1920.
- **`isometric-pastel` (04-02):** animação isométrica nas cores do tema.
- **Narração no VSL (04-03):** legenda da narração e áudio original, por opção (`--captions`, `--audio`).
- **Contraste (04-04):** a cor do texto segue o fundo do estilo, com contraste mínimo.
- **Cores do design system (04-05):** o estilo só anima; as cores vêm do tema.

### 03 — Enquadramento automático do corte (2026-11-16)
- **Layout automático:** `cut` escolhe sozinho `fill` (pessoa), `zoom` (tela com atividade) ou `fit`, sem parâmetro. Extra opcional `vision` (OpenCV) para detectar rosto e atividade; sem ele, `fit`.
- **Zoom no tempo:** a região acompanha a ação dentro do corte; fundo na cor do tema e legenda `lower-third` abaixo do conteúdo.
- **Glossário:** `correcoes.json` corrige termos errados da transcrição (frases de tamanhos diferentes) antes da legenda e do prompt.
- **Folga e fade:** 0,40 s antes e 0,70 s depois da fala, com fade de vídeo e áudio.
- **Região por densidade:** o zoom tem a proporção da faixa do conteúdo (1080×920) e escolhe o tamanho pela cobertura da atividade.
- **Cobertura da transcrição e do corte:** `av<17` fixado, `--file`/`--style` aceitos, aviso se faltar o filtro `ass`, modelo `medium`/`large-v3`, `initial_prompt` e variantes regionais no glossário.
- **Limitações conhecidas (C5):** cortes sobre a tela toda ficam em `fit` (aceito quando a fala é sobre ela; o critério é atividade, não fala); a região não troca no tempo; o Dock pode aparecer. Calibrar limiares de rosto, histerese, folga e fade com mais vídeos.
