import { Scene, Transition } from "./types";

/** Duração de cada transição entre cenas: metade na saída e metade na entrada. */
export const TRANSITION_SECONDS = 0.35;

export type SceneSpan = {
  from: number; duration: number;
  /** Transição da cena anterior que entra aqui (null: corte seco ou primeira cena). */
  inKind: Transition | null;
  /** Transição desta cena para a próxima (null: corte seco ou última cena). */
  outKind: Transition | null;
};

/** Quadros de cada fase (saída ou entrada) da transição. */
export const halfFrames = (fps: number): number => Math.max(1, Math.round((TRANSITION_SECONDS / 2) * fps));

/** Limites de cada cena na linha do tempo; as checagens de quadros usam estes mesmos números. */
export const timeline = (scenes: Scene[], fps: number): SceneSpan[] => {
  let cursor = 0;
  return scenes.map((scene, i) => {
    const duration = Math.round(scene.dur * fps);
    const kind = (s: Scene | undefined): Transition | null => (s?.transition && s.transition !== "cut" ? s.transition : null);
    const span = { from: cursor, duration, inKind: kind(scenes[i - 1]), outKind: i < scenes.length - 1 ? kind(scene) : null };
    cursor += duration;
    return span;
  });
};

/** Quadros da transição entre a cena `i` e a seguinte: fim da saída e início da entrada. */
export const boundary = (spans: SceneSpan[], i: number, fps: number) => {
  const half = halfFrames(fps);
  const end = spans[i].from + spans[i].duration;
  return { outStart: end - half, outEnd: end, inStart: end, inEnd: end + half };
};

/** Quanto da cena está visível (0 a 1) no quadro local `frame`: sai e entra de forma escalonada. */
export const presence = (span: SceneSpan, frame: number, fps: number, ease: (t: number) => number): number => {
  const half = halfFrames(fps);
  const enter = span.inKind ? ease(frame / half) : 1;
  const leave = span.outKind ? 1 - ease((frame - (span.duration - half)) / half) : 1;
  return Math.min(1, Math.max(0, Math.min(enter, leave)));
};
