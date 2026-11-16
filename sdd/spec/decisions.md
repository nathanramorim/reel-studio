# Decisões — reel-studio

## Resolvidas

| # | Decisão | Resolução | Motivo |
|---|---------|-----------|--------|
| R1 | Base da arquitetura | ADR-0001 | Tokens baixos, dados locais, replicável |
| R2 | Voz ruim | Limpar local primeiro; TTS só com licença comercial validada | XTTS (Coqui) é não comercial |
| R3 | Avatar | Avatar estilizado com rhubarb (MIT) | Local, CPU, sem biometria em nuvem |
| R4 | Fontes dos estilos | Cópia local em `styles/`, Atlas só como origem | Site pode sair do ar |

## Abertas

| # | Questão |
|---|---------|
| D1 | Provedor TTS com clone de voz e licença comercial |
| D2 | Prompts originais do Style Atlas: colar em `styles/*/style.md` |
| D3 | Cores finais dos temas pessoal e busize |
