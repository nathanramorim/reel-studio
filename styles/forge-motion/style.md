# Forge Motion

## Visual
Linguagem de movimento do vídeo do pipeline do Forge: painéis de terminal (janela com barra e pontos), pacotes luminosos que percorrem o fluxo, cartões com borda superior colorida, texto em degradê e fundo vivo (grade deslizando e brilho que respira). Termos técnicos saem em fonte mono.

## Como os componentes aplicam o tema
O estilo só anima: toda cor vem dos tokens do tema (`accent`, `accent2`, `success`, `gradient`, `surface`, `muted`). O bloco `brand` do tema define raio, borda e pontos do painel e o brilho do pacote. Sem `brand`, os painéis usam os valores padrão.

## Zona segura
Todo conteúdo fica entre y 250 e 1536, com guarda lateral de 140 px (`render/src/safeZone.ts`).
