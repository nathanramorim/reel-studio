import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme, Style } from "../types";
import { fontFamily } from "../fonts";
import { SCALE } from "../scale";

export const Chart: React.FC<{
  values: { label: string; value: number }[]; theme: Theme; style: Style;
}> = ({ values, theme, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  const max = Math.max(...values.map((v) => v.value), 1);
  const grow = Math.min(1, frame / (fps * 0.8));
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", alignItems: "flex-end",
      justifyContent: "center", gap: 28, padding: "0 90px 220px",
    }}>
      {values.map((v, i) => (
        <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 72, height: (v.value / max) * 480 * grow, background: accent, borderRadius: 10,
          }} />
          <div style={{
            fontFamily: fontFamily(theme.fonts.body), fontSize: SCALE.min, color: theme.colors.text, textAlign: "center",
          }}>{v.label}</div>
        </div>
      ))}
    </div>
  );
};
