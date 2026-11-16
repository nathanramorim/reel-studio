import React from "react";
import { Theme } from "../types";
import { panelSpec } from "./panel";

/** Cartão com borda superior colorida (linguagem do vídeo do Forge). */
export const Card: React.FC<{
  theme: Theme; accent: string; opacity?: number; offsetX?: number; reveal?: number; children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ theme, accent, opacity = 1, offsetX = 0, reveal, children, style }) => (
  <div data-reveal-at={reveal} style={{
    opacity, transform: `translateX(${offsetX}px)`, background: theme.colors.surface,
    borderTop: `6px solid ${accent}`, borderRadius: panelSpec(theme).radius,
    padding: "22px 32px", ...style,
  }}>
    {children}
  </div>
);
