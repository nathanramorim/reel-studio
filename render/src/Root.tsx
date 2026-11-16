import React from "react";
import { Composition } from "remotion";
import { Reel } from "./Reel";
import { Overlay } from "./overlay/Overlay";
import { OverlayProps, ReelProps } from "./types";
import sample from "../sample-props.json";

const DEFAULT_PROPS = sample as unknown as ReelProps;

const totalFrames = (props: ReelProps) =>
  Math.max(1, Math.round(props.scenes.reduce((sum, s) => sum + s.dur, 0) * props.fps));

const OVERLAY_DEFAULTS: OverlayProps = {
  overlays: [], theme: DEFAULT_PROPS.theme, style: DEFAULT_PROPS.style, fps: DEFAULT_PROPS.fps, length: 1,
};

export const RemotionRoot: React.FC = () => (
  <>
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
    <Composition
      id="Overlay"
      component={Overlay}
      width={1080}
      height={1920}
      fps={OVERLAY_DEFAULTS.fps}
      durationInFrames={Math.max(1, Math.round(OVERLAY_DEFAULTS.length * OVERLAY_DEFAULTS.fps))}
      defaultProps={OVERLAY_DEFAULTS}
      calculateMetadata={({ props }) => ({
        durationInFrames: Math.max(1, Math.round(props.length * props.fps)),
        fps: props.fps,
      })}
    />
  </>
);