import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme } from "../types";

const CELL = 90;

/** Fundo do tema com grade deslizando e brilho que respira; função só do quadro global. */
export const LiveBackground: React.FC<{ theme: Theme }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const shift = (t * 20) % CELL;
  const breathe = 0.85 + 0.15 * Math.sin(t * 1.6);
  const line = `${theme.colors.muted}0d`;
  return (
    <div style={{ position: "absolute", inset: 0, background: theme.colors.bg }}>
      <div style={{
        position: "absolute", inset: 0, opacity: breathe,
        background: `radial-gradient(ellipse at 50% 25%, ${theme.colors.glow ?? theme.colors.bg} 0%, transparent 65%)`,
      }} />
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(${line} 1px, transparent 1px), linear-gradient(90deg, ${line} 1px, transparent 1px)`,
        backgroundSize: `${CELL}px ${CELL}px`, backgroundPosition: `${shift}px ${shift}px`,
      }} />
    </div>
  );
};
