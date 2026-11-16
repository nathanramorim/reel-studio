# Discovery 05 — VSL premium (linguagem de movimento do tema + regras do /brag)

## Problema
O VSL entregue pela iniciativa 04 já tem fontes, cores do tema, narração e contraste, mas ainda parece fraco ("caixas aparecendo com fade"). O C6 (clip-05, tema forge) mostrou:
- a legenda e as placas caem na zona que a interface de Reels, TikTok e Shorts cobre;
- as placas são blocos 3D, e não isométricas de verdade;
- não há linguagem de movimento: sem fluxo que se mova, sem texto sincronizado com a fala, sem câmera, sem transições, sem trilha;
- nada da identidade que o Forge-SDD já tem no vídeo do pipeline (`forge-sdd/docs/video-pipeline/video.html`): painéis tipo terminal, pacotes luminosos, cartões com borda colorida, texto em degradê, brilho e grade, mascote, trilha própria.

## Para quem
Quem gera reels no modo VSL com o design system de um projeto (primeiro usuário: o autor, tema forge) e quer um vídeo que pareça feito à mão, para postar.

## Referência
Regras de criação e acabamento adaptadas do `/brag` (`latent-spaces/brag`, licença MIT; usamos as ideias do `brag-slim`, sem a dependência Hyperframes). Os créditos entram no README. O que já temos é reaproveitado (tabela em `criteria.md`).

## Jornada
1. A pessoa pede o VSL do corte (tom opcional: `default`, `polished`, `cinematic`…).
2. O agente escreve o roteiro com gancho, 2 a 3 destaques e fecho, e a copy para postar.
3. O render monta cenas com a linguagem do tema (painéis, pacotes, texto que acompanha a fala), transições limpas e, por opção, trilha na batida.
4. Sai o mp4 com o pôster no quadro 0, mais o `share-copy.txt`.

## Regras de negócio
- **Cores e identidade vêm do tema** (design system do projeto); o estilo só define a gramática do movimento (decisão da 04).
- **Zona segura da vertical:** o que se lê fica entre 13% e 80% da altura (y 250 a 1536) e fora dos 140 px da direita na metade de baixo.
- **Leitura:** a linha a ler fica inteira e parada por cerca de 0,3 s por palavra.
- **Gancho** nos 2 primeiros segundos; cada quadro parado deve valer o post.
- **Transição limpa:** sai o antigo, entra o novo, ou passa pelo fundo; nunca dupla exposição.
- **Cada quadro é função do tempo** (determinístico); fontes e imagens carregadas antes de capturar.
- **Mostrar a coisa:** quando houver gravação, a cena pode trazer um painel com o trecho real, em vez de só abstração.
- **Privacidade:** nada de segredo, token, e-mail ou nome de cliente no vídeo ou na copy; gravação com dado sensível gera aviso.
- LLM nunca vê mídia; dados e render locais; sem rede no render.

## Escopo
**Dentro:** zona segura e tempo de leitura; kit da marca no tema; estilo `forge-motion` (painéis, pacotes, texto em degradê, fundo e câmera vivos); texto sincronizado com a narração; transições; roteiro estilo brag (gancho, tom, copy); trilha e efeitos na batida (opcional); painel com o trecho real; QA de quadros do meio da transição, pôster e `share-copy.txt`.
**Fora:** voz sintética (TTS), Hyperframes ou outro renderizador, publicação automática, novos temas além do ajuste do `forge`.

## Riscos
| Risco | Mitigação |
|---|---|
| Escopo grande | Quatro ondas; cada feature entrega valor sozinha; `forge-motion` primeiro |
| Render lento com câmera, brilho e vários painéis | Medir no C6; limitar efeitos por cena; cache de fundo |
| Trilha sintetizada soar amadora | Opcional (`--music`); reaproveitar o `musica.py` já aprovado do Forge |
| Texto sincronizado quebrar sem tempos de palavra | Fallback: distribuir as palavras pelo tempo da cena |
| Painel com gravação vazar dado sensível | Aviso e verificação antes de usar o trecho real |
| Licença do `/brag` | MIT; adaptar com créditos, sem copiar código de terceiros |
