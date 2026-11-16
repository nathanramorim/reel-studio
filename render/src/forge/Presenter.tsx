import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme } from "../types";

/** Há fala em `t` (s)? Intervalos relativos ao corte, vindos de core/cut.py (`speech`). */
export const speaking = (speech: [number, number][] | undefined, t: number): boolean =>
  (speech ?? []).some(([a, b]) => t >= a && t <= b);

/** Apresentador: o mascote do tema, que balança e pulsa enquanto há fala e fica parado sem ela. */
export const Presenter: React.FC<{
  theme: Theme; speech?: [number, number][]; left: number; top: number; size: number; opacity?: number;
}> = ({ theme, speech, left, top, size, opacity = 1 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const uri = theme.brand?.mascotUri;
  if (!uri) return null;
  const t = frame / fps;
  const talking = speaking(speech, t);
  const bob = talking ? Math.sin(t * 9) * 6 : 0;
  const pulse = talking ? 1 + 0.04 * Math.abs(Math.sin(t * 9)) : 1;
  return (
    <img data-presenter="" src={uri} style={{
      position: "absolute", left, top, width: size, height: size, objectFit: "contain", opacity,
      transform: `translateY(${bob}px) scale(${pulse})`,
    }} />
  );
};
