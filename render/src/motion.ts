import { interpolate, spring } from "remotion";

/** Entrada em pop (escala) ou slide (posição), conforme style.look.motion. */
export const popIn = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

export const fadeIn = (frame: number, from: number, to: number) =>
  interpolate(frame, [from, to], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
