# ADR-0006: O prompt para a IA usa um script determinístico

- **Data:** 2026-11-19
- **Status:** `proposto` (vira `aprovado` com o merge humano do PR da iniciativa 07)
- **Regras afetadas (IDs da constitution):** `ARQ-12` (nova)
- **Autor / Responsável:** dono do repositório

## Contexto

É comum o README trazer um prompt para colar na IA antes de instalar: a IA confere os requisitos e, se faltar algo, já considera instalar. Um prompt solto ("veja se tem ffmpeg, Node, Whisper...") depende de qual IA lê e muda a cada execução. A constitution não dizia nada sobre facilidade de uso nem sobre esse prompt (feature `feat-07-01`).

## Opções Consideradas

1. **Só o prompt no README:** simples, mas a IA improvisa os comandos e pode aceitar licenças ou mexer em chaves sem querer.
2. **Script determinístico + prompt que usa o script:** `scripts/requisitos.py checar` e `instalar` fazem a parte repetível; o prompt só manda rodar o script e pedir o ok da pessoa.

## Decisão

Opção 2. Nova regra `ARQ-12`: todo desenvolvimento considera a facilidade de uso e um prompt para a IA; o que dá para fazer de forma determinística vira script, e o prompt usa o script como ferramenta. O script nunca aceita licença, consentimento ou declaração pela pessoa e nunca lê segredos.

## Consequências

- **Positivas:** a instalação dá o mesmo resultado com qualquer IA; o que falta aparece numa tabela com o comando exato; licenças e chaves ficam com a pessoa.
- **Negativas / Trade-offs:** a receita precisa acompanhar os requisitos reais (extras, versão do Remotion, modelos); quando mudar um requisito, mude o `requisitos.toml` e rode `requisitos.py prompt` para o README.
- **Atualização (feat-07-02):** o script próprio deu lugar ao motor multiplataforma `requisitos-para-ia` vendorizado (`scripts/requisitos.py`, `bootstrap.sh`, `bootstrap.ps1`; origem e commit no `skills.lock`), com a receita declarativa em `requisitos.toml`. A decisão (prompt usa script determinístico) continua a mesma.
- **Ações de acompanhamento:** manter `engine/tests/test_requisitos.py` atualizado quando um requisito mudar.
