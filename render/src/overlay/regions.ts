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
  /** Moldura ao redor da faixa do conteúdo (mesma faixa do `fit` e do `zoom` em core/cut.py). */
  frame: { top: 320, height: 920 },
  /** Faixa acima da legenda: chips e callouts empilham de baixo para cima. */
  strip: { bottom: CAPTION.top - 10, slot: 110 },
  /** Rodapé abaixo da legenda: barra de progresso, logo e CTA. */
  footer: { top: CAPTION.bottom + 20, height: 140 },
} as const;

export const SIDE = 140;
export const OVERLAY_FADE_SECONDS = 0.25;
