# Discovery 05 — Reels premium: componentes sobre o vídeo real e VSL com a linguagem do tema

## Problema
O C6 do VSL (clip-05, tema forge) ficou fraco: legenda e placas na zona que a interface de Reels cobre, placas que são blocos 3D e não isométricas, e nenhuma linguagem de movimento. O Forge-SDD já tem essa linguagem no vídeo do pipeline (`forge-sdd/docs/video-pipeline/video.html`): painéis tipo terminal, pacotes luminosos, cartões com borda colorida, texto em degradê, brilho e grade, mascote e trilha.

Ao mesmo tempo, o modo **corte** já ficou bom no uso real (enquadramento, legenda, voz e corte). Isso não pode se perder: o premium se soma ao que funciona.

## Para quem
Quem grava a tela ou a si mesmo e quer postar reels com a identidade do próprio projeto. Primeiro usuário: o autor, tema forge.

## Entradas (o que a pessoa traz)
| Entrada | Exemplo | Saída | Voz | Música |
|---|---|---|---|---|
| **Vídeo pronto** | gravação de tela | **Corte com componentes** (vídeo real mais camadas), ou VSL a partir do vídeo | A voz gravada, sempre que houver | Opcional; desligada por padrão |
| **Vídeo sem áudio** | gravação de tela muda | Corte com componentes, ou VSL | Opcional: voz gerada a partir de uma gravação sua | **Ligada por padrão** |
| **Conteúdo** | texto, README, URL, projeto | VSL animado com a linguagem do tema | Opcional: voz gerada a partir de uma gravação sua; sem referência, sem voz | **Ligada por padrão** |
| **Livre** | só uma ideia | VSL animado | Igual ao conteúdo | **Ligada por padrão** |

**Voz gerada a partir de gravação:** a pessoa indica uma gravação da própria voz (ou o próprio vídeo); o motor extrai uma amostra limpa e sintetiza a narração das cenas nessa voz, localmente. Serve também ao VSL de vídeo com áudio ruim: a mesma pessoa, com o roteiro re-narrado em voz limpa. A síntese sem voz de referência (voz genérica) fica fora desta iniciativa.

## Mantido (não regredir)
Estas partes foram validadas no uso real e continuam como estão:
- **Enquadramento automático do corte** (`fill` por rosto, `zoom` por densidade, `fit`), com a escolha por vídeo e a mesma saída do `ffmpeg` para as mesmas entradas.
- **Legenda palavra a palavra** no `lower-third`, com o tema e a posição de hoje.
- **A voz original** do vídeo no corte e no VSL a partir de vídeo, e o glossário de correções.
- **Folga de fala e fade** do corte.
As novas camadas entram **sobre** esse resultado e só quando pedidas ou pertinentes; sem elas, o corte sai idêntico ao de hoje.

## Referência
Regras de criação e acabamento adaptadas do `/brag` (`latent-spaces/brag`, licença MIT, ideias do `brag-slim`, sem Hyperframes), com créditos no README.

## Jornada
1. A pessoa traz um vídeo, um conteúdo ou só uma ideia (tom opcional: `default`, `polished`, `cinematic`…).
2. Com vídeo: o corte sai como hoje, e o agente propõe as camadas de componentes a partir da transcrição (gancho, palavras-chave, passos, CTA). Sem vídeo: o agente escreve o roteiro com gancho, destaques e fecho.
3. O render compõe: no corte, a camada de componentes por cima do vídeo real; no VSL, as cenas na linguagem do tema, com texto que acompanha a fala.
4. Sai o mp4 com pôster no quadro 0 e o `share-copy.txt`.

## Regras de negócio
- **Cores e identidade vêm do tema**; o estilo só define a gramática do movimento (decisão da 04).
- **Camadas sobre o corte, nunca no lugar dele:** o corte (ffmpeg) segue intocado, e os componentes entram numa camada transparente compositada por cima.
- **Voz:** com vídeo, a voz original é o padrão; no VSL a partir de vídeo, o áudio original passa a ser o padrão quando todas as cenas têm `source`, e a legenda também.
- **Música:** ligada por padrão quando não há áudio de voz (vídeo mudo, conteúdo, livre) e desligada quando há voz; com voz (gravada ou gerada), a trilha fica sempre abaixo dela (ducking).
- **Voz gerada (clone):** só a partir de gravação indicada pela pessoa, que confirma ser a própria voz (ou ter autorização); processamento local; a marca d'água do modelo é mantida; a amostra e o áudio gerado nunca vão para log ou rede. A duração de cada cena segue o áudio gerado, e os tempos de palavra (texto e legenda) vêm de transcrever esse áudio com o próprio Whisper local.
- **Zona segura da vertical** para o que é novo: texto lido entre 13% e 80% da altura (y 250 a 1536) e fora dos 140 px da direita na metade de baixo. A legenda do corte continua onde está (já fica nessa zona).
- **Leitura:** linha a ler fica inteira e parada por cerca de 0,3 s por palavra.
- **Gancho** nos 2 primeiros segundos; cada quadro parado deve valer o post.
- **Transição limpa:** sai o antigo, entra o novo, ou passa pelo fundo; nunca dupla exposição.
- **Cada quadro é função do tempo**; fontes e imagens carregadas antes de capturar.
- **Mostrar a coisa:** com gravação, a tela real aparece dentro das cenas do VSL, em uma janela, com o recorte automático.
- **Privacidade:** nada de segredo, token, e-mail ou nome de cliente no vídeo ou na copy; gravação com dado sensível gera aviso.
- LLM nunca vê mídia; dados e render locais; sem rede no render.

## Escopo
**Dentro:** música por padrão sem áudio; voz gerada a partir de gravação (clone local, opcional); contrato das camadas (`overlays`) e das entradas conteúdo e livre; corte com componentes; zona segura e tempo de leitura; kit da marca no tema; estilo `forge-motion` para o VSL; texto sincronizado com a fala; transições; janela com a tela real nas cenas do VSL; roteiro estilo brag (gancho, tom, copy); trilha opcional na batida, com a voz em primeiro plano; QA, pôster e `share-copy.txt`.
**Fora:** voz sintética sem gravação de referência, Hyperframes ou outro renderizador, publicação automática, novos temas além do ajuste do `forge`, mudar o enquadramento, a legenda ou o corte atuais.

## Riscos
| Risco | Mitigação |
|---|---|
| Camada de componentes alterar o corte aprovado | Composição por cima do mp4 do corte; teste que o comando do corte não muda sem camadas |
| Componentes tapando o conteúdo da tela | Áreas reservadas (topo, faixa acima da legenda) e a zona segura; checagem por quadros |
| Escopo grande | Quatro ondas; o corte com componentes vem primeiro, é onde está o valor imediato |
| Render lento (câmera, brilho, painéis) | Medir no C8; limitar efeitos; camada transparente curta |
| Camada transparente aumentar o peso | Formato com alfa só durante a composição, descartado no fim |
| Texto sincronizado sem tempos de palavra | Fallback: distribuir as palavras pelo tempo da cena |
| Trilha cobrir a voz | Ducking: a voz sempre à frente; trilha opcional |
| Licença do `/brag` | MIT; só ideias, com créditos |
| Clonar a voz sem consentimento | A amostra vem de gravação indicada pela pessoa, com confirmação explícita; marca d'água mantida; nada vai para a rede |
| Modelo de voz pesado e lento, e qualidade em pt-BR | Extra opcional `tts`; modelo baixado uma vez, fora do render; candidato Chatterbox (MIT, pt-BR); validar no C11 e medir o tempo |
| Tempo da fala gerada não bater com a cena | A cena segue o áudio gerado; tempos de palavra por transcrição local |
