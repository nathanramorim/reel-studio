# ADR-0005: Constitution no padrão de skill replicável (Forge SDD 4.9.1-beta)

- **Data:** 2026-11-19
- **Status:** `proposto` (vira `aprovado` com o merge humano do PR "chore: adota Forge SDD")
- **Regras afetadas (IDs da constitution):** `FLX-01`, `FLX-02`, `FLX-07`, `ARQ-03`, `ARQ-04`, `SEG-04`, `SEG-05`, `COD-02`, `TST-01`, `GOV-01`, `GOV-02`
- **Autor / Responsável:** dono do repositório

## Contexto

Toda skill é um repositório próprio e replicável, com estrutura Forge SDD, `/constitution` alinhada e README pelo readme-studio com `## Requisitos`; toda nova feature ou fix passa pelo fluxo Forge para mapear execuções, criar histórico e sequencializar contexto. A constitution do reel-studio (Forge 4.8.0) tinha regras genéricas do template e não dizia isso.

## Opções Consideradas

1. **Manter as regras do template:** não cobre replicabilidade, uv, README nem o fluxo obrigatório.
2. **Reescrever as 15 regras para o domínio, consolidando as genéricas:** mantém o limite de 15.

## Decisão

Opção 2, com atualização da estrutura para Forge 4.9.1-beta:
- Regras 1, 2 e 15 antigas viram a Regra 1 (branch por iniciativa); a Regra 2 nova exige `/discovery`, `/nova-feature` ou `/novo-fix` para toda feature ou fix.
- Regra 3 (replicável), Regra 6 (uv + ruff + pytest, junta as antigas 6 e 7), Regra 7 (local por padrão; só texto vai ao LLM), Regra 12 (README pelo readme-studio com `## Requisitos`) e Regra 15 (aprovação humana do JSON antes de `cut`/`render`) são novas ou reescritas.
- A Regra 11 (beta fora da `main`) continua; a estrutura 4.9.1-beta entra com exceção `GOV-02` registrada em `sdd/discovery/06-adocao-forge/discovery.md`.

## Consequências

- **Positivas:** uma regra por decisão real do projeto; o Reviewer audita contra regras verificáveis.
- **Negativas / Trade-offs:** temas e estilo com nomes reais (`pessoal`, `busize`, `forge`, `forge-motion`) passam a divergir da Regra 3 até uma feature removê-los (registrado em "Divergências conhecidas").
- **Ações de acompanhamento:** `/nova-feature` para tirar os temas reais da skill e trocar o tema padrão `pessoal` da CLI; `/novo-fix` para o README atender ao verificador do readme-studio.
