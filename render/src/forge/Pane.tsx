import React from "react";
import { Theme } from "../types";
import { panelSpec } from "./panel";

const BAR = 44;
const DOT = 14;

/** Janela de terminal: barra com pontos e corpo; raio, borda e pontos vêm do `brand` do tema. */
export const Pane: React.FC<{
  theme: Theme; accent: string; opacity?: number; reveal?: number; children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ theme, accent, opacity = 1, reveal, children, style }) => {
  const spec = panelSpec(theme);
  const dotColors = [theme.colors.bad ?? accent, theme.colors.warn ?? accent, theme.colors.success ?? accent,
    theme.colors.accent2 ?? accent, accent];
  return (
    <div data-panel="" data-reveal-at={reveal} style={{
      opacity, background: theme.colors.surface, borderRadius: spec.radius,
      border: `2px solid ${spec.border}`, overflow: "hidden", display: "flex", flexDirection: "column",
      boxShadow: `0 0 40px ${theme.colors.glow ?? "transparent"}`, ...style,
    }}>
      {spec.bar && (
        <div style={{
          height: BAR, display: "flex", alignItems: "center", gap: 10, padding: "0 18px",
          borderBottom: `2px solid ${spec.border}`, flexShrink: 0,
        }}>
          {Array.from({ length: spec.dots }, (_, i) => (
            <div key={i} style={{ width: DOT, height: DOT, borderRadius: "50%", background: dotColors[i % dotColors.length] }} />
          ))}
        </div>
      )}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", padding: "10px 28px" }}>
        {children}
      </div>
    </div>
  );
};
