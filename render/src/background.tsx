import React from "react";
import { Theme, Style } from "./types";

/** O fundo do estilo, ou o fundo do tema quando o estilo pede "theme" (ADR-0001). */
export const sceneBackground = (theme: Theme, style: Style): string =>
  style.background === "own" && style.look.bg ? style.look.bg : theme.colors.bg;

/** Fundo do tema com o brilho radial a 50% x 25% (como no banner do Forge); sem `glow`, só o `bg`. */
const withGlow = (theme: Theme, base: string): string =>
  theme.colors.glow
    ? `radial-gradient(ellipse at 50% 25%, ${theme.colors.glow} 0%, transparent 65%), ${base}`
    : base;

export const Background: React.FC<{ theme: Theme; style: Style }> = ({ theme, style }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: style.background === "own" ? sceneBackground(theme, style)
        : withGlow(theme, sceneBackground(theme, style)),
    }}
  />
);
