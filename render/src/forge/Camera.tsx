import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { easeOut } from "../motion";

const DRIFT = 0.04;
const SECONDS = 6;

/** Avanço suave por cena: escala de 1 a 1,04 em 6 s, função só do quadro local da cena. */
export const Camera: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = 1 + DRIFT * easeOut(frame / (SECONDS * fps));
  return <div style={{ position: "absolute", inset: 0, transform: `scale(${scale})` }}>{children}</div>;
};
