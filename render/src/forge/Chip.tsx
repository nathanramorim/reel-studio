import React from "react";
import { Theme } from "../types";
import { fontFamily } from "../fonts";
import { SCALE } from "../scale";
import { monoFont } from "./panel";

/** Pílula de texto curto em mono (termos técnicos); `ink` é a cor do texto sobre o preenchimento. */
export const Chip: React.FC<{
  theme: Theme; fill: string; ink: string; opacity?: number; children: React.ReactNode;
}> = ({ theme, fill, ink, opacity = 1, children }) => (
  <span style={{
    opacity, background: fill, color: ink, borderRadius: 999, padding: "8px 24px",
    fontFamily: fontFamily(monoFont(theme)), fontSize: SCALE.secondary, fontWeight: 500,
  }}>
    {children}
  </span>
);
