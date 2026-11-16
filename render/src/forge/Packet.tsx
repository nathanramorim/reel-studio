import React from "react";
import { Theme } from "../types";
import { packetSpec } from "./panel";

const SIZE = 28;

/** Pílula com glow que percorre o trecho vertical `from`..`to` (px) no progresso `progress` (0 a 1). */
export const Packet: React.FC<{
  theme: Theme; color: string; x: number; from: number; to: number; progress: number;
}> = ({ theme, color, x, from, to, progress }) => {
  const spec = packetSpec(theme);
  const visible = progress > 0 && progress < 1;
  return (
    <div style={{
      position: "absolute", left: x - SIZE / 2, top: from + (to - from) * progress - SIZE / 2,
      width: SIZE, height: SIZE, borderRadius: spec.radius, background: color,
      opacity: visible ? 1 : 0, boxShadow: spec.glow ? `0 0 24px 6px ${color}` : "none",
    }} />
  );
};
