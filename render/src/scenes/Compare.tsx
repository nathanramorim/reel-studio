import React from "react";
import { Theme, Style, SidePoints } from "../types";

const Side: React.FC<{ side?: SidePoints; theme: Theme; accent: string }> = ({
  side, theme, accent,
}) => (
  <div style={{
    flex: 1, background: theme.colors.surface, borderRadius: 20, padding: 28,
    border: `2px solid ${theme.colors.muted}22`,
  }}>
    <div style={{
      fontFamily: theme.fonts.title, fontWeight: 800, fontSize: 32, color: accent, marginBottom: 16,
    }}>
      {side?.label ?? ""}
    </div>
    {(side?.points ?? []).map((p, i) => (
      <div key={i} style={{
        fontFamily: theme.fonts.body, fontSize: 26, color: theme.colors.text, marginBottom: 10,
      }}>
        — {p}
      </div>
    ))}
  </div>
);

export const Compare: React.FC<{
  left?: SidePoints; right?: SidePoints; theme: Theme; style: Style;
}> = ({ left, right, theme, style }) => {
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  const accent2 = style.look.palette?.[1] ?? theme.colors.accent2 ?? accent;
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", flexDirection: "column",
      gap: 24, padding: "180px 60px",
    }}>
      <Side side={left} theme={theme} accent={accent} />
      <Side side={right} theme={theme} accent={accent2} />
    </div>
  );
};
