import React from "react";
import { Composition } from "remotion";
import { Reel } from "./Reel";
import { ReelProps } from "./types";
import sample from "../sample-props.json";

const DEFAULT_PROPS = sample as unknown as ReelProps;

const totalFrames = (props: ReelProps) =>
  Math.max(1, Math.round(props.scenes.reduce((sum, s) => sum + s.dur, 0) * props.fps));

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel}
    width={1080}
    height={1920}
    fps={DEFAULT_PROPS.fps}
    durationInFrames={totalFrames(DEFAULT_PROPS)}
    defaultProps={DEFAULT_PROPS}
    calculateMetadata={({ props }) => ({
      durationInFrames: totalFrames(props),
      fps: props.fps,
    })}
  />
);
