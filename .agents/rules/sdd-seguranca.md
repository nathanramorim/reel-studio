---
description: Como aplicar validação de entrada, proteção de arquivos de domínio, higiene de segredos/logs e governança de dependências.
globs: ["**/*"]
regras: [SEG-01, SEG-02, SEG-04, SEG-05, SEG-07]
---

# Guia Prático — Segurança, Segredos e Dependências

Procedimentos práticos para atender aos IDs `SEG-01`, `SEG-02`, `SEG-04`, `SEG-05` e `SEG-07` de `sdd/memory/constitution.md` (`GOV-04`).

## 1. Validação de Borda e Escrita Segura (`SEG-01`, `SEG-02`)

- **Saneamento de entradas (`SEG-01`):**
  - Valide flags obrigatórias, enums permitidos (ex.: `--style`, `--theme`, `--captions`, `--audio`) e schemas JSON antes de iniciar mutações em arquivos.
  - Rejeite identificadores ou slugs que contenham `..`, separadores de diretório inesperados ou caracteres de controle.
- **Preservação de domínio (`SEG-02`):**
  - Toda escrita do motor fica na pasta de trabalho do vídeo (`core/project.py`, `core/paths.py`) ou na saída pedida; nunca sobrescreve o vídeo de origem. Processos externos (`ffmpeg`, `whisper`) recebem argumentos em lista, sem shell (`SEG-03`, `core/proc.py`).

- **Local por padrão:** vídeo, áudio e transcrição completa nunca saem da máquina; só o texto compactado vai ao LLM, e o OpenRouter só no caminho de automação, com `OPENROUTER_API_KEY` no `.env` (fora do git).

## 2. Prevenção de Vazamento de Segredos e Dados Sensíveis (`SEG-04`, `SEG-05`)

- **Higiene do repositório e templates (`SEG-04`):**
  - Em testes e exemplos de documentação/templates, utilize placeholders claramente fictícios (`<SEU_TOKEN_AQUI>`, `example-token-placeholder`) — nunca chaves reais ou strings com formato de token de provedor (`ghp_`, `sk-`, `AKIA`, `BEGIN PRIVATE KEY`).
- **Logs, erros e telemetria (`SEG-05`):**
  - Mensagens de erro e arquivos em `sdd/.metrics/` devem registrar apenas metadados operacionais (comando, duração, status, caminho relativo da feature), sem despejar variáveis de ambiente ou cabeçalhos de autenticação.

## 3. Avaliação de Dependências Externas (`SEG-07`)

- Antes de alterar `engine/pyproject.toml` (`uv add`) ou `render/package.json`:
  1. Confirme se a biblioteca padrão ou uma dependência já presente não atende (`ARQ-04`); se for pesada, vira extra opcional.
  2. Caso indispensável, verifique o status do MCP `context7` em `sdd/memory/mcps.md` (ou consulte a documentação oficial na versão exata).
  3. Preencha a seção `## Dependências novas` na Spec da feature indicando nome do pacote, versão exata, licença e motivo pelo qual o que já existe não atende. Se não houver novas bibliotecas, registre explicitamente `Nenhuma.` nessa seção.
