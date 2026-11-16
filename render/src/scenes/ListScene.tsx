import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme, Style } from "../types";
import { fadeIn } from "../motion";

export const ListScene: React.FC<{ items: string[]; theme: Theme; style: Style }> = ({
  items, theme, style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  const perItem = Math.max(6, Math.floor(fps * 0.6));
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", flexDirection: "column",
      justifyContent: "center", gap: 28, padding: "0 110px",
    }}>
      {items.map((item, i) => {
        const opacity = fadeIn(frame, i * perItem, i * perItem + 8);
        return (
          <div key={i} style={{
            opacity, transform: `translateX(${(1 - opacity) * -24}px)`,
            display: "flex", alignItems: "center", gap: 20,
            fontFamily: theme.fonts.body, fontSize: 40, fontWeight: 600, color: theme.colors.text,
          }}>
            <span style={{ color: accent, fontSize: 32 }}>●</span>
            {item}
          </div>
        );
      })}
    </div>
  );
};
