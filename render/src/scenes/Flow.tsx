import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme, Style } from "../types";
import { fadeIn } from "../motion";
import { fontFamily } from "../fonts";
import { SCALE } from "../scale";

/** Passo a passo: caixas em coluna ligadas por setas, no acento do estilo/tema. */
export const Flow: React.FC<{ steps: string[]; theme: Theme; style: Style }> = ({
  steps, theme, style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  const perStep = Math.max(8, Math.floor((fps * 0.8)));
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", gap: 20, padding: "0 100px",
    }}>
      {steps.map((step, i) => {
        const opacity = fadeIn(frame, i * perStep, i * perStep + 10);
        return (
          <React.Fragment key={i}>
            <div style={{
              opacity, transform: `translateY(${(1 - opacity) * 20}px)`,
              background: theme.colors.surface, border: `2px solid ${accent}`,
              borderRadius: 16, padding: "18px 32px", color: theme.colors.text,
              fontFamily: fontFamily(theme.fonts.title), fontWeight: 700, fontSize: SCALE.body,
              display: "flex", alignItems: "center", gap: 16,
            }}>
              <span style={{
                background: accent, color: theme.colors.bg, borderRadius: "50%",
                width: 72, height: 72, display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: SCALE.min,
              }}>{i + 1}</span>
              {step}
            </div>
            {i < steps.length - 1 && (
              <div style={{ opacity, color: accent, fontSize: SCALE.min }}>↓</div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
