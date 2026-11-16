import { interpolate, spring } from "remotion";

/** Entrada em pop (escala) ou slide (posição), conforme style.look.motion. */
export const popIn = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

export const fadeIn = (frame: number, from: number, to: number) =>
  interpolate(frame, [from, to], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

/** Easing cúbico de saída do Forge (cubic-bezier .16,1,.3,1 aproximado por 1-(1-t)^3). */
export const easeOut = (t: number): number => 1 - Math.pow(1 - Math.min(Math.max(t, 0), 1), 3);

/** Mola do Forge: entrada com leve overshoot, função só do quadro. */
export const springForge = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 120, mass: 0.8 } });

/** Atraso em quadros do item `i` numa entrada escalonada (0,18 s por item). */
export const stagger = (i: number, fps: number, step = 0.18): number => Math.round(i * step * fps);
