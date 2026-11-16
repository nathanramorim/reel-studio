import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme, Style } from "../types";
import { popIn } from "../motion";
import { fitFontSize } from "../text-fit";

export const Title: React.FC<{ text: string; theme: Theme; style: Style }> = ({
  text, theme, style,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const scale = popIn(frame, fps);
  const size = fitFontSize(text, width - 160, 96, 48);
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", alignItems: "center",
      justifyContent: "center", padding: "0 80px", textAlign: "center",
    }}>
      <div style={{
        fontFamily: theme.fonts.title, fontWeight: 700, fontSize: size,
        color: theme.colors.text, lineHeight: 1.15, transform: `scale(${scale})`,
      }}>
        {text.split(" ").map((word, i) => (
          <span key={i} style={i % 3 === 1 ? { color: accent } : undefined}>
            {word}{" "}
          </span>
        ))}
      </div>
    </div>
  );
};
