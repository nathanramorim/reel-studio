import React from "react";
import { Sequence, AbsoluteFill } from "remotion";
import { ReelProps } from "./types";
import { Background } from "./background";
import { SceneRenderer } from "./SceneRenderer";
import { useThemeFonts } from "./fonts";
import { Probe } from "./probe";
import { LiveBackground } from "./forge/LiveBackground";

export const Reel: React.FC<ReelProps> = ({ scenes, theme, style, fps, probe }) => {
  useThemeFonts(theme);
  const live = style.look.motion === "forge";
  const families = [...new Set([theme.fonts.title, theme.fonts.body, ...(live && theme.fonts.mono ? [theme.fonts.mono] : [])])];
  let frameCursor = 0;
  return (
    <AbsoluteFill id="probe-root">
      {live && <LiveBackground theme={theme} />}
      {probe && <Probe families={families} />}
      {scenes.map((scene, i) => {
        const from = frameCursor;
        const durationInFrames = Math.round(scene.dur * fps);
        frameCursor += durationInFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={durationInFrames}>
            {!live && <Background theme={theme} style={style} />}
            <SceneRenderer scene={scene} theme={theme} style={style} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
