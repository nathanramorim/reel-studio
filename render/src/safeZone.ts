/** Zona segura da vertical 1080×1920 (DUP-03): fora dela a interface da plataforma cobre o conteúdo. */
export const SAFE = {
  top: 250,
  bottom: 1536,
  /** Guarda lateral direita (botões da plataforma), só na metade de baixo. */
  rightGuard: 140,
  /** Início da metade de baixo do quadro. */
  lowerHalf: 960,
} as const;

/** Altura útil entre o topo e a base da zona segura. */
export const SAFE_HEIGHT = SAFE.bottom - SAFE.top;

/** Borda direita do conteúdo, respeitando a guarda para qualquer altura. */
export const safeRight = (width: number): number => width - SAFE.rightGuard;

/** Folga interna da área de conteúdo: a câmera do `forge-motion` amplia até 4% e o texto não sai da zona. */
export const CAMERA_MARGIN = 40;
/** Margem lateral do conteúdo (guarda de 140 px mais folga da câmera). */
export const SIDE_MARGIN = SAFE.rightGuard + 20;
