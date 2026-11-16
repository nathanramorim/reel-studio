import React from "react";
import { Theme, Style } from "../types";
import { fontFamily } from "../fonts";
import { SCALE } from "../scale";

export const Cta: React.FC<{ text?: string; theme: Theme; style: Style }> = ({
  text, theme, style,
}) => {
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", gap: 20, padding: "0 100px", textAlign: "center",
    }}>
      <div style={{
        fontFamily: fontFamily(theme.fonts.title), fontWeight: 800, fontSize: SCALE.titleMax, color: theme.colors.text,
      }}>
        {text ?? theme.cta.text}
      </div>
      <div style={{
        fontFamily: fontFamily(theme.fonts.title), fontWeight: 700, fontSize: SCALE.secondary, color: accent,
      }}>
        {theme.cta.handle ?? ""}
      </div>
    </div>
  );
};
