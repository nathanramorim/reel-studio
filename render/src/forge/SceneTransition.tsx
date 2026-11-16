import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { easeOut } from "../motion";
import { SceneSpan, halfFrames, presence } from "../timeline";
import { Transition } from "../types";

const SLIDE = 120;

const style = (kind: Transition, p: number, entering: boolean): React.CSSProperties => {
  if (kind === "wipe") {
    const hidden = `${(1 - p) * 100}%`;
    return { clipPath: entering ? `inset(0 ${hidden} 0 0)` : `inset(0 0 0 ${hidden})` };
  }
  if (kind === "slide") {
    const dx = (1 - p) * SLIDE * (entering ? 1 : -1);
    return { opacity: p, transform: `translateX(${dx}px)` };
  }
  return { opacity: p };
};

/** Sai o conteúdo antigo e entra o novo, em fases separadas (a soma das presenças nunca passa de 1). */
export const SceneTransition: React.FC<{ span: SceneSpan; index: number; children: React.ReactNode }> = ({
  span, index, children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const half = halfFrames(fps);
  const leaving = span.outKind !== null && frame >= span.duration - half;
  const kind = leaving ? span.outKind : span.inKind;
  const p = presence(span, frame, fps, easeOut);
  const css = kind && p < 1 ? style(kind, p, !leaving) : {};
  return (
    <div data-scene={index} data-presence={p} style={{ position: "absolute", inset: 0, ...css }}>
      {children}
    </div>
  );
};
