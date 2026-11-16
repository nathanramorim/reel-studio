import React from "react";
import { Sequence, AbsoluteFill } from "remotion";
import { ReelProps } from "./types";
import { Background } from "./background";
import { SceneRenderer } from "./SceneRenderer";
import { useThemeFonts } from "./fonts";
import { Probe } from "./probe";

export const Reel: React.FC<ReelProps> = ({ scenes, theme, style, fps, probe }) => {
  useThemeFonts(theme);
  let frameCursor = 0;
  return (
    <AbsoluteFill id="probe-root">
      {probe && <Probe families={[theme.fonts.title, theme.fonts.body]} />}
      {scenes.map((scene, i) => {
        const from = frameCursor;
        const durationInFrames = Math.round(scene.dur * fps);
        frameCursor += durationInFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={durationInFrames}>
            <Background theme={theme} style={style} />
            <SceneRenderer scene={scene} theme={theme} style={style} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
