import React, { useEffect, useState } from "react";
import { continueRender, delayRender } from "remotion";

const textWidth = (font: string, weight: string): number => {
  const ctx = document.createElement("canvas").getContext("2d");
  if (!ctx) return 0;
  ctx.font = `${weight} 100px ${font}`;
  return ctx.measureText("Reel Studio Montserrat 0123456789").width;
};

/** Só para `scripts/check-render.mjs`: mede fonte carregada e menor texto, e loga em JSON. */
export const Probe: React.FC<{ families: string[] }> = ({ families }) => {
  const [handle] = useState(() => delayRender("probe"));
  useEffect(() => {
    document.fonts.ready.then(() => {
      const fonts = families.map((family) => ({
        family,
        loaded: document.fonts.check(`700 20px "${family}"`),
        width: textWidth(`"${family}", sans-serif`, "700"),
        serifWidth: textWidth("serif", "700"),
      }));
      const sizes: number[] = [];
      document.querySelectorAll<HTMLElement>("#probe-root *").forEach((el) => {
        const hasText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent?.trim());
        if (hasText) sizes.push(parseFloat(getComputedStyle(el).fontSize));
      });
      console.log(`[probe] ${JSON.stringify({ fonts, minSize: sizes.length ? Math.min(...sizes) : null })}`);
      continueRender(handle);
    });
  }, []);
  return null;
};
