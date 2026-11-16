import React from "react";
import { Theme, Style } from "./types";

/** O fundo do estilo, ou o fundo do tema quando o estilo pede "theme" (ADR-0001). */
export const sceneBackground = (theme: Theme, style: Style): string =>
  style.background === "own" && style.look.bg ? style.look.bg : theme.colors.bg;

export const Background: React.FC<{ theme: Theme; style: Style }> = ({ theme, style }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: sceneBackground(theme, style),
    }}
  />
);
