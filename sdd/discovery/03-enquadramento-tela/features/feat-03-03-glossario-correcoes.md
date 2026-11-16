# feat-03-03-glossario-correcoes — Correção automática de termos errados na transcrição

## Modelo do módulo
completo

## Decisões do projeto aplicadas
ADR-0001 (domínio em `core/`, CLI na borda; transcrição local, LLM só vê texto compactado). `concepts.md`: novo dono `core/glossary.py` (Glossário), registrado na entrega (`DUP-01`).

## O que já existe
| Procurei | Onde | Achei | Decisão | Justificativa |
|---|---|---|---|---|
| Transcrição | `core/transcribe.py`, `cli._transcript` | `transcript.json` cru, sem correção | estender | `_transcript` aplica o glossário em memória para todos os consumidores |
| Legenda | `core/captions.build_ass` | usa `words_in(transcript)` | reusar | Recebe a transcrição já corrigida; sem mudança de assinatura |
| Texto para o LLM | `core/compact.py` | compacta a transcrição | reusar | Ganha o texto corrigido sem alteração |
| Tema | `themes/*.json`, `contracts/theme.schema.json` | sem glossário | estender | Campo opcional `glossary` (fallback) |
| Glossário de referência | `forge-sdd/gravacoes/correcoes.json` e `corrigir()` | mapa errado→certo; troca só com mesmo nº de palavras | criar | Generalizar para frases de tamanho diferente |

## Dependências novas
Nenhuma.

## Rules e IDs da Constituição Aplicáveis
SEG-01, SEG-02, ARQ-05, ARQ-06, ARQ-10, DUP-01, TST-01

## Contexto do defeito
- **Origem:** `feat-01-02-transcrever` e `feat-01-04-cortar-legenda`.
- **Causa-raiz:** o Whisper erra termos do domínio e o `cut` queima o texto cru. Nada lê um glossário.
- **Evidência:** `Forge STD` (Forge SDD), `fitres` (features), `Plane` (Plan), `QEJ-Zone` em duas palavras (queue.json) e `assete` (aceite) foram para a legenda.

## Escopo
- **Arquivo:** `correcoes.json`, mapa `"frase errada": "frase certa"`. Chaves que começam com `_` são comentário. O arquivo fica no repo do usuário.
- **Onde procura (o mais específico vence):** `--glossary <arquivo>`; `correcoes.json` na pasta do vídeo e nas pastas acima, até a raiz do repositório git (o `forge-sdd/gravacoes/correcoes.json` fica achado a partir do vídeo); `correcoes.json` na pasta de trabalho do vídeo; campo opcional `glossary` do tema.
- **Casamento:** por palavras inteiras, ignorando maiúsculas, acentos de caixa e pontuação (inclusive hífen: `QEJ -Zone` casa `QEJ-Zone`). Frase errada e certa podem ter tamanhos diferentes; vale a frase mais longa primeiro. A substituição não é reaplicada sobre si mesma.
- **Tempos:** o trecho trocado ocupa do início da primeira ao fim da última palavra original; as palavras novas dividem esse intervalo proporcionalmente ao tamanho. A pontuação final da última palavra original é preservada. Espaços sobrando nos valores são removidos.
- **Aplicação:** em memória, em `cli._transcript`, para `cut`, `prompt-suggest` e `prompt-script`; `transcript.json` em disco continua cru (`ARQ-05`). O texto de cada segmento também é corrigido.
- **Aviso:** o `cut` imprime quantas correções aplicou e de qual arquivo veio o glossário.
- **Validação (`SEG-01`):** JSON de objeto, só strings, até 256 KB e 2000 entradas; inválido dá erro com o caminho do arquivo. Só leitura (`SEG-02`).

## Critérios de Aceitação Executáveis
- `cd engine && uv run pytest tests/test_glossary.py`:
  - os 5 casos do relato (`Forge STD`→`Forge SDD`, `fitres`→`features`, `Plane`→`Plan`, `QEJ -Zone`→`queue.json`, `assete`→`aceite`) corrigem `words` e `text`;
  - troca de 2 palavras por 1 e de 1 por 2 mantém `start`/`end` coerentes e sem sobreposição;
  - ignora caixa e pontuação e preserva a pontuação final;
  - precedência: `--glossary` vence a pasta do vídeo, que vence o tema;
  - arquivo inválido ou grande demais é rejeitado.
- `uv run pytest tests/test_cut.py -k glossario`: `build_ass` recebe a transcrição corrigida e o `.ass` contém `Forge SDD`.
- `uv run reel-studio cut "<gravação>" --theme forge --dry-run` informa o glossário e o nº de correções e não escreve nada.
- `cd engine && uv run pytest && uv run ruff check` passam.
