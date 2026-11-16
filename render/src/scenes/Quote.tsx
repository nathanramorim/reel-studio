import React from "react";
import { Theme, Style } from "../types";
import { fontFamily } from "../fonts";
import { titleSize } from "../scale";

export const Quote: React.FC<{ text: string; theme: Theme; style: Style }> = ({
  text, theme, style,
}) => {
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", alignItems: "center",
      justifyContent: "center", padding: "0 120px",
    }}>
      <div style={{
        fontFamily: fontFamily(theme.fonts.title), fontStyle: "italic", fontWeight: 700,
        fontSize: titleSize(text, 800), color: theme.colors.text, textAlign: "center",
      }}>
        <span style={{ color: accent, fontSize: "1.4em" }}>&ldquo;</span>
        {text}
        <span style={{ color: accent, fontSize: "1.4em" }}>&rdquo;</span>
      </div>
    </div>
  );
};
