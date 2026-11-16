import { SAFE } from "../safeZone";

/**
 * Áreas reservadas da camada de componentes sobre o corte (1080×1920).
 * A legenda `lower-third` fica entre `CAPTION.top` e `CAPTION.bottom` (margem vertical 560 de
 * core/captions.py, `MARGIN_V`; o check-render confere essa constante).
 */
export const CAPTION = { top: 1180, bottom: 1360 } as const;

export const REGIONS = {
  /** Topo: gancho e título. */
  hook: { top: SAFE.top + 20, height: 260 },
  /** Faixa acima da legenda: chips e callouts empilham de baixo para cima. */
  strip: { bottom: CAPTION.top - 10, slot: 110 },
  /** Faixa abaixo do gancho (`pos: "top"`): chips e callouts empilham de cima para baixo. */
  topStrip: { top: SAFE.top + 20 + 260 + 10, slot: 110 },
  /** Rodapé abaixo da legenda: barra de progresso, logo e CTA. */
  footer: { top: CAPTION.bottom + 20, height: 140 },
} as const;

/** Layout `split` (core/cut.py `SPLIT_Y`, `SPLIT_H`): vídeo em y 250 a 950; texto só abaixo dele. */
export const SPLIT = {
  video: { top: 250, bottom: 950 },
  hook: { top: 970, height: 100 },
  chip: { top: 1075, height: 95 },
  /** Rodapé: apresentador à esquerda, logo à direita, CTA e barra no meio. */
  presenter: { size: 150 },
} as const;

export const SIDE = 140;
export const OVERLAY_FADE_SECONDS = 0.25;
