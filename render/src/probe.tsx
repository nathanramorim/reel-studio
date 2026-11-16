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
      const boxes: { top: number; bottom: number; left: number; right: number; scene?: number; presence?: number }[] = [];
      document.querySelectorAll<HTMLElement>("#probe-root *").forEach((el) => {
        const texts = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent?.trim());
        if (!texts.length) return;
        sizes.push(parseFloat(getComputedStyle(el).fontSize));
        texts.forEach((node) => {
          const range = document.createRange();
          range.selectNodeContents(node);
          const r = range.getBoundingClientRect();
          const holder = el.closest<HTMLElement>("[data-presence]");
          boxes.push({
            top: r.top, bottom: r.bottom, left: r.left, right: r.right,
            scene: holder ? Number(holder.dataset.scene) : undefined,
            presence: holder ? Number(holder.dataset.presence) : undefined,
          });
        });
      });
      const rect = (el: Element) => { const r = el.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, left: r.left, right: r.right }; };
      const reveals = [...document.querySelectorAll<HTMLElement>("#probe-root [data-reveal-at]")].map((el) => ({
        at: Number(el.dataset.revealAt), opacity: Number(getComputedStyle(el).opacity), text: el.textContent ?? "",
      }));
      const media = [...document.querySelectorAll("#probe-root [data-media-box]")].map(rect);
      const minSize = sizes.length ? Math.min(...sizes) : null;
      console.log(`[probe] ${JSON.stringify({ fonts, minSize, boxes, reveals, media })}`);
      continueRender(handle);
    });
  }, []);
  return null;
};
