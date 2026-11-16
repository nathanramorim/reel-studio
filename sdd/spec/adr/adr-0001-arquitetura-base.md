# ADR-0001: Arquitetura base do reel-studio

- **Status:** aceita
- **Data:** 2026-11-16

## Contexto

O autor grava vídeos explicando processos e quer reels para o Instagram sem ferramenta SaaS. Requisitos: replicável (outras pessoas instalam e usam a própria marca), baixo consumo de tokens e dados locais.

## Decisão

1. **O LLM só lê texto.** Vídeo e áudio nunca vão para o modelo. A transcrição é compactada em linhas `[segundos] texto` antes de sair.
2. **Contratos JSON entre as etapas:** `transcript.json`, `clips.json` (modo corte) e `scenes.json` (modo VSL). Os schemas ficam em `contracts/`.
3. **Cenas por componentes prontos.** O LLM escolhe tipo de cena e parâmetros; quem desenha são os componentes de cada estilo (Remotion ou Manim). Nada de código gerado por vídeo.
4. **Estilo e tema são eixos separados.** Estilo = linguagem visual (`styles/`). Tema = marca: cores, fontes, logo, CTA (`themes/`). Qualquer combinação é válida.
5. **Distribuição como plugin do Claude Code** (skill + comandos), sem MCP: a skill só entra no contexto quando é usada.
6. **Layout Python:** `cli.py` é a borda (papel do `cmd/` em `ARQ-01`) e `core/` é o domínio (papel do `internal/`).
7. **Modo semiautomático:** a IA sugere cortes e cenas, a pessoa aprova o JSON antes do render.

## Consequências

- Uma chamada de LLM por vídeo (cerca de 1 a 2 mil tokens por reel).
- Novos estilos exigem componentes; novos temas exigem só um JSON.
- Remotion tem licença paga para empresas acima de 3 pessoas: documentado no README.
