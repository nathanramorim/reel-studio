# Estilos (modo VSL)

Origem: [AI Style Atlas](https://www.futurepedia.io/resources/ai-style-atlas/view), copiado para `styles/` deste plugin — se o site cair, nada quebra aqui.

| Estilo | Melhor para | Render |
|---|---|---|
| `flat-vector-science` | Conceitos e metáforas | Remotion |
| `whiteboard-explainer` | Raciocínio passo a passo | Remotion |
| `isometric-pastel` | Processos e fluxos | Remotion |
| `forge-motion` | VSL técnico: painéis de terminal, pacotes luminosos, degradê, fundo vivo | Remotion |
| `manim-style-math` | Números, gráficos e fórmulas | Manim (fase 3, ainda não renderiza) |

Cada estilo só aceita alguns tipos de cena (campo `scene_types` em `styles/<id>/style.json`). O comando `script` já valida isso.

Para adicionar um estilo novo: crie `styles/<id>/style.json` seguindo `contracts/style.schema.json` e um `style.md` com a origem. Novos componentes de cena vão em `render/src/scenes/`.
