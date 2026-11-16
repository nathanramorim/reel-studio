import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme, Style } from "../types";
import { popIn } from "../motion";
import { fontFamily } from "../fonts";
import { titleSize } from "../scale";

export const Highlight: React.FC<{ text: string; theme: Theme; style: Style }> = ({
  text, theme, style,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const scale = popIn(frame, fps);
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  const size = titleSize(text, width - 200);
  return (
    <div style={{
      position: "absolute", inset: 0, display: "flex", alignItems: "center",
      justifyContent: "center", padding: "0 100px",
    }}>
      <div style={{
        fontFamily: fontFamily(theme.fonts.title), fontWeight: 800, fontSize: size,
        color: theme.colors.text, textAlign: "center", transform: `scale(${scale})`,
        borderLeft: `8px solid ${accent}`, paddingLeft: 32,
      }}>
        {text}
      </div>
    </div>
  );
};
