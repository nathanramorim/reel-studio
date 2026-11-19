# Discovery 06 — Adoção do padrão Forge SDD de skill

## Problema
O reel-studio já usava Forge SDD 4.8.0, mas a constitution tinha regras genéricas do template e não dizia que a skill é replicável, que Python é só `uv`, que toda feature ou fix passa pelo fluxo Forge nem que o README segue o readme-studio com `## Requisitos`.

## O que muda (só governança e documentação, nenhum código do motor)
- Estrutura atualizada para Forge 4.9.1-beta (`forge update --upgrade`), agente gemini adicionado (`GEMINI.md`, `.gemini/`), telemetria ligada.
- Constitution: missão, stack, decisões e 15 regras do domínio (ADR-0005); divergências reais registradas.
- `sdd/spec/`: módulos, stack, fluxos (exemplos com `acme`) e índice de ADRs atualizados; ADR-0004 (uv, retrodocumentada) e ADR-0005.
- Rules de `.agents/rules/` adaptadas de Go para Python/TypeScript.
- `.gitignore`: sessões de telemetria e runtime fora do git (repositório público).

## Modelo do módulo
`enxuto`: docs e configuração do Forge; nenhum estado de domínio.

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Estrutura Forge | `sdd/`, `.agents/`, `.claude/` | 4.8.0 instalada | estender | `forge update --upgrade`, sem reinstalar |
| Decisão de arquitetura | `sdd/spec/adr/adr-0001-arquitetura-base.md` | LLM só texto, contratos, plugin, aprovação humana | reusar | As regras 7, 10 e 15 citam a ADR-0001 |

## Dependências novas
Nenhuma.

## Exceção (`GOV-02`)
A Regra 11 proíbe mesclar versão `-beta` na `main`, e a estrutura instalada é do Forge 4.9.1-beta. As outras skills (carrossel-studio, agendador-mk-studio) não têm exceção registrada; esta é a primeira.

```constitution-exception
regra: Regra 11 (FLX-07)
motivo: estrutura Forge SDD 4.9.1-beta instalada nesta branch; o merge na main depende desta exceção ou da versão estável do Forge
prazo: 2026-12-31
responsavel: dono do repositório (nathanramorim)
```

## Critérios
1. `forge brief --check` reporta `pronta`.
2. `forge gate` sem falha bloqueante.
3. `git ls-files sdd/.metrics` lista só `schema.json`.
