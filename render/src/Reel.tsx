import React from "react";
import { Sequence, AbsoluteFill } from "remotion";
import { ReelProps } from "./types";
import { Background } from "./background";
import { SceneRenderer } from "./SceneRenderer";

export const Reel: React.FC<ReelProps> = ({ scenes, theme, style, fps }) => {
  let frameCursor = 0;
  return (
    <AbsoluteFill>
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
