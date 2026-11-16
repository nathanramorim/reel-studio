import React from "react";

const COS30 = Math.cos(Math.PI / 6);
const SIN30 = 0.5;

const mix = (hex: string, target: number, amount: number): string => {
  const n = parseInt(hex.replace("#", ""), 16);
  const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((c) =>
    Math.round(c + (target - c) * amount),
  );
  return `rgb(${ch.join(",")})`;
};

/** Desloca a extrusão da placa nos eixos isométricos (projeção de 30°). */
export const isoOffset = (depth: number) => ({ dx: depth * COS30, dy: depth * SIN30 });

export type SlabProps = {
  x: number; y: number; w: number; h: number; color: string;
  depth?: number; opacity?: number; lift?: number; children?: React.ReactNode;
};

/**
 * Placa isométrica: frente legível, topo e lateral direita extrudados a 30°,
 * três tons por face e sombra longa projetada para baixo e à direita.
 */
export const IsoSlab: React.FC<SlabProps> = ({
  x, y, w, h, color, depth = 40, opacity = 1, lift = 0, children,
}) => {
  const { dx, dy } = isoOffset(depth);
  const top = mix(color, 255, 0.45);
  const side = mix(color, 0, 0.22);
  const shadow = "rgba(40,30,60,0.14)";
  const s = 70 * COS30;
  const t = 70 * SIN30;
  return (
    <div style={{
      position: "absolute", left: x, top: y + lift, width: w + dx, height: h + dy, opacity,
    }}>
      <svg width={w + dx + s} height={h + dy + t} style={{ position: "absolute", left: 0, top: -dy, overflow: "visible" }}>
        <polygon fill={shadow}
          points={`0,${h + dy} ${w},${h + dy} ${w + dx},${h} ${w + dx + s},${h + t} ${w + s},${h + dy + t} ${s},${h + dy + t}`} />
        <polygon points={`0,${dy} ${dx},0 ${w + dx},0 ${w},${dy}`} fill={top} />
        <polygon points={`${w},${dy} ${w + dx},0 ${w + dx},${h} ${w},${h + dy}`} fill={side} />
        <rect x={0} y={dy} width={w} height={h} fill={color} />
      </svg>
      <div style={{
        position: "absolute", left: 0, top: 0, width: w, height: h,
        display: "flex", alignItems: "center", boxSizing: "border-box",
      }}>
        {children}
      </div>
    </div>
  );
};
