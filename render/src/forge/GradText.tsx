import React from "react";
import { Theme } from "../types";
import { gradientStops } from "./panel";

/** Texto em degradê do tema (`colors.gradient`); a cor do glifo é o próprio degradê. */
export const GradText: React.FC<{ theme: Theme; children: React.ReactNode }> = ({ theme, children }) => (
  <span style={{
    backgroundImage: `linear-gradient(90deg, ${gradientStops(theme).join(", ")})`,
    WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
    WebkitTextFillColor: "transparent",
  }}>
    {children}
  </span>
);
