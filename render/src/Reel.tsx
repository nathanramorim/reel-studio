import React from "react";
import { Sequence, AbsoluteFill } from "remotion";
import { ReelProps } from "./types";
import { Background } from "./background";
import { SceneRenderer } from "./SceneRenderer";
import { useThemeFonts } from "./fonts";
import { Probe } from "./probe";
import { LiveBackground } from "./forge/LiveBackground";
import { SceneTransition } from "./forge/SceneTransition";
import { timeline } from "./timeline";

export const Reel: React.FC<ReelProps> = ({ scenes, theme, style, fps, probe }) => {
  useThemeFonts(theme);
  const live = style.look.motion === "forge";
  const families = [...new Set([theme.fonts.title, theme.fonts.body, ...(live && theme.fonts.mono ? [theme.fonts.mono] : [])])];
  const spans = timeline(scenes, fps);
  return (
    <AbsoluteFill id="probe-root">
      {live && <LiveBackground theme={theme} />}
      {probe && <Probe families={families} />}
      {scenes.map((scene, i) => {
        const span = spans[i];
        return (
          <Sequence key={i} from={span.from} durationInFrames={span.duration}>
            {!live && <Background theme={theme} style={style} />}
            <SceneTransition span={span} index={i}>
              <SceneRenderer scene={scene} theme={theme} style={style} />
            </SceneTransition>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
