# Discovery 04 — VSL: áudio e estilo visual

## Problema
No modo VSL (clip-05 da gravação 14.33.02, tema forge, estilo `isometric-pastel`):
- **11. Sem áudio:** o mp4 sai só com vídeo. O `Reel.tsx` não tem `<Audio>`, o `render.py` não passa áudio, e a `narration` das cenas não vira fala nem legenda.
- **12. Estilo sem identidade:** fundo preto liso (`background: "theme"` + tema escuro), fonte em serifa (nenhum código carrega a Montserrat), fonte pequena para 1080×1920 (36 a 56 px), bloco no meio com o resto vazio, `flow` só com caixas e setas verticais, nada isométrico nem pastel.

## Para quem
Quem usa o modo VSL (vídeo ou áudio ruim) e espera um vídeo que se entenda sem o original.

## Jornada
1. A pessoa pede o VSL do corte.
2. O motor renderiza as cenas no estilo, com fontes carregadas e o quadro bem usado.
3. O vídeo traz a narração de alguma forma (decisão pendente) e sai legível no celular.

## Regras de negócio
- O vídeo VSL tem de ser compreensível sozinho: a narração precisa estar no vídeo, como fala ou como legenda.
- Estilo e tema continuam combináveis (ADR-0001): o estilo define a linguagem visual; o tema entrega acento, fontes e CTA.
- Dados locais: nada de rede no render (fontes empacotadas, não baixadas).
- O LLM nunca vê mídia.

## Escopo
**Dentro:** carregamento local das fontes do tema, escala tipográfica para 1080×1920, `isometric-pastel` com visual isométrico e pastel, aproveitamento do quadro; narração no VSL.
**Fora:** TTS com clone de voz (fase 3 do discovery 01), novos estilos, Manim.

## Decisão (humano): A e C, cada um por opção
A voz sintética (B) fica para a fase 3. Abaixo, as opções avaliadas.
| Opção | O que é | Prós | Contras |
|---|---|---|---|
| A. Áudio original do corte | Recorta o áudio da gravação e o toca no VSL | Voz real | As cenas reescrevem a fala (33 s de cenas para 56 s de fala); só alinha se cada cena tiver o trecho de origem; o VSL existe para quando o áudio é ruim |
| B. Voz sintética (TTS) | Gera fala da `narration` | VSL autônomo | Dependência e modelo novos; é fase 3 |
| C. Legendar a `narration` | Queima a narration como legenda no ritmo das cenas | Sem dependência; funciona com áudio ruim; reaproveita o `.ass` e o tema | Sem fala |

**Recomendação:** C como padrão, e A como opção (`--audio original`) só quando as cenas trouxerem `source: {start, end}` do trecho de origem. B fica para a fase 3.

## Riscos
| Risco | Mitigação |
|---|---|
| Fonte empacotada aumenta o repositório | Só os pesos usados; licença OFL junto |
| Visual isométrico pesado em CSS | Slabs por componente único, sem imagens |
| Texto claro sobre fundo claro | `look.ink` do estilo define a cor do texto |
