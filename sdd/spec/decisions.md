# Decisões — reel-studio

## Resolvidas

| # | Decisão | Resolução | Motivo |
|---|---------|-----------|--------|
| R1 | Base da arquitetura | ADR-0001 | Tokens baixos, dados locais, replicável |
| R2 | Voz ruim | Limpar local primeiro; TTS só com licença comercial validada | XTTS (Coqui) é não comercial |
| R3 | Avatar | Avatar estilizado com rhubarb (MIT) | Local, CPU, sem biometria em nuvem |
| R4 | Fontes dos estilos | Cópia local em `styles/`, Atlas só como origem | Site pode sair do ar |
| R5 | Python | Sempre `uv` (`uv sync`, `uv run`, `uv add`); nunca pip | ADR-0004 |
| R6 | Constitution realinhada ao padrão de skill | Fluxo Forge para toda feature/fix, replicável, uv, README com `## Requisitos` | ADR-0005 |

## Índice de ADRs

| ADR | Título | Status |
|-----|--------|--------|
| ADR-0001 | Arquitetura base | aceita |
| ADR-0002 | `doctor` (branch da iniciativa 02, não vigente) | — |
| ADR-0003 | Modelo de voz (branch `feat/05-vsl-premium`, PR #5) | — |
| ADR-0004 | Python sempre via uv | aprovado |
| ADR-0005 | Constitution no padrão de skill replicável (Forge SDD 4.9.1-beta) | proposto |

## Abertas

| # | Questão |
|---|---------|
| D1 | Provedor TTS com clone de voz e licença comercial |
| D2 | Prompts originais do Style Atlas: colar em `styles/*/style.md` |
| D3 | Temas reais do autor (`pessoal`, `busize`, `forge`) saem do repositório da skill (Divergência em `constitution.md`) |
