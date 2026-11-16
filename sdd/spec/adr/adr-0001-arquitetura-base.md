# ADR-0001: Arquitetura base do reel-studio

- **Status:** aceita
- **Data:** 2026-11-16

## Contexto

O autor grava vídeos explicando processos e quer reels para o Instagram sem ferramenta SaaS. Requisitos: replicável (outras pessoas instalam e usam a própria marca), baixo consumo de tokens e dados locais.

## Decisão

1. **O LLM só lê texto.** Vídeo e áudio nunca vão para o modelo. A transcrição é compactada em linhas `[segundos] texto` antes de sair.
2. **Dentro do Claude Code, quem gera o JSON é o agente, não uma chamada de rede nova.** A CLI expõe `prompt-suggest`/`prompt-script` (mostram o prompt) e `save-clips`/`save-scenes` (validam e gravam o JSON que o agente escreveu). `suggest`/`script` chamam o OpenRouter de verdade e existem só para automação fora de uma sessão com agente (CI, cron).
3. **Contratos JSON entre as etapas:** `transcript.json`, `clips.json` (modo corte) e `scenes.json` (modo VSL). Os schemas ficam em `contracts/`.
4. **Cenas por componentes prontos.** O LLM (agente ou automação) escolhe tipo de cena e parâmetros; quem desenha são os componentes de cada estilo (Remotion ou Manim). Nada de código gerado por vídeo.
5. **Estilo e tema são eixos separados.** Estilo = linguagem visual (`styles/`). Tema = marca: cores, fontes, logo, CTA (`themes/`). Qualquer combinação é válida.
6. **Distribuição como plugin do Claude Code** (skill + comandos), sem MCP: a skill só entra no contexto quando é usada.
7. **Layout Python:** `cli.py` é a borda (papel do `cmd/` em `ARQ-01`) e `core/` é o domínio (papel do `internal/`).
8. **Modo semiautomático:** a IA sugere cortes e cenas, a pessoa aprova o JSON antes do render.
9. **Compatível com qualquer agente que leia skills (`DUP-10`).** A fonte única da skill de produto é `skills/reel-studio/`, porque é essa a estrutura exigida pelo plugin do Claude Code. `.agents/skills/reel-studio/SKILL.md` (lido pelo agy/Antigravity) e `AGENTS.md` na raiz (lido pelo Codex) são adaptadores finos: cada um aponta para `skills/reel-studio/SKILL.md` e suas `references/`, sem repetir o conteúdo. Os temas e os temas de exemplo são do autor; qualquer pessoa cria os seus (`themes/exemplo.json`).

## Consequências

- Dentro do Claude Code: zero chamada de rede extra e zero chave de API para escolher cortes ou escrever o roteiro.
- No caminho de automação (sem agente): uma chamada ao OpenRouter por vídeo (cerca de 1 a 2 mil tokens por reel).
- Novos estilos exigem componentes; novos temas exigem só um JSON.
- Remotion tem licença paga para empresas acima de 3 pessoas: documentado no README.
