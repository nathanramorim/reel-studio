# ADR-0003: Modelo de voz gerada (clone local, extra `tts`)

- **Data:** 2026-11-16
- **Status:** `proposto` (aguarda a validação manual C12 com a gravação 14.33.02)
- **Regras afetadas (IDs da constitution):** `ARQ-04`, `SEG-05`, `SEG-07`
- **Autor / Responsável:** Builder (iniciativa 05, `feat-05-11`)

## Contexto

O VSL com voz da própria pessoa precisa de síntese que clone a voz a partir de uma amostra da gravação, em português, sem enviar áudio para fora da máquina. O áudio gerado define a duração das cenas e os tempos de palavra (`feat-05-06`).

## Opções Consideradas

1. **Chatterbox (`resemble-ai/chatterbox`, `chatterbox-tts` 0.1.7):** MIT (código e pacote), clona de amostra, multilíngue com `language_id="pt"`, roda em `cpu`/`mps`/`cuda`, marca d'água embutida. Pesos baixados do Hugging Face na instalação.
2. **Serviço de voz em nuvem:** melhor qualidade, mas envia a voz para fora (`SEG-05`) e exige chave.
3. **Sem voz gerada (só voz original e trilha):** nenhuma dependência, mas o VSL sem gravação fica mudo.

## Decisão

Opção 1, como extra opcional `tts` (`uv sync --extra tts`), com import tardio em `core/voice.py` (`ChatterboxMultilingualTTS.from_pretrained(device=...)`; `generate(texto, language_id, audio_prompt_path)`). API conferida na documentação oficial do repositório (o context7 não estava exposto à sessão do Builder). Versão travada no `uv.lock` (0.1.7); o checkpoint multilíngue padrão é o legado (V2); trocar para `t3_model="v3"` exige versão do pacote que o exponha.

Salvaguardas: consentimento explícito (`--confirm-own-voice`), sem referência não há voz, amostra e áudio só na pasta do vídeo, nada em log, marca d'água mantida, modelo nunca baixado durante o render.

## Consequências

- **Positivas:** voz própria offline; dependência pesada isolada num extra; os testes usam sintetizador simulado e não baixam o modelo.
- **Negativas / Trade-offs:** extra grande (torch); o `uv.lock` cresceu e alguns pacotes foram re-resolvidos; qualidade pt-BR e tempo por cena só medidos no C12 (manual); licença dos pesos no Hugging Face a reconfirmar antes de publicar vídeos.
- **Ações de acompanhamento:** executar o C12 e promover esta ADR a `aprovado` ou trocar de modelo.
