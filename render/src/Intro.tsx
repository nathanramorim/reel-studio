import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { IntroProps } from "./types";
import { fontFamily, useThemeFonts } from "./fonts";
import { SAFE } from "./safeZone";
import { titleSize } from "./scale";
import { easeOut, springForge } from "./motion";
import { LiveBackground } from "./forge/LiveBackground";
import { GradText } from "./forge/GradText";

const WIDTH = 1080;
const SIDE = 140;

/** Abertura do corte: fundo vivo, logo e gancho em degradê; função só do quadro, sem áudio. */
export const Intro: React.FC<IntroProps> = ({ text, theme, fps }) => {
  useThemeFonts(theme);
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const enter = Math.min(1, springForge(frame, fps, 0));
  const textIn = Math.min(1, springForge(frame, fps, Math.round(0.25 * fps)));
  const out = easeOut(Math.min(1, Math.max(0, (durationInFrames - frame) / (0.3 * fps))));
  const logo = theme.brand?.logoUri;
  const width = WIDTH - 2 * SIDE;
  return (
    <AbsoluteFill id="probe-root" style={{ opacity: out }}>
      <LiveBackground theme={theme} />
      {logo && (
        <img src={logo} style={{
          position: "absolute", left: (WIDTH - 220) / 2, top: SAFE.top + 220, width: 220, height: 220,
          objectFit: "contain", opacity: enter, transform: `scale(${0.6 + 0.4 * enter})`,
        }} />
      )}
      <div style={{
        position: "absolute", left: SIDE, width, top: SAFE.top + 520, textAlign: "center",
        opacity: textIn, transform: `translateY(${(1 - textIn) * 40}px)`,
        fontFamily: fontFamily(theme.fonts.title), fontWeight: 800, lineHeight: 1.15,
        fontSize: titleSize(text, width),
      }}>
        <GradText theme={theme}>{text}</GradText>
      </div>
    </AbsoluteFill>
  );
};
