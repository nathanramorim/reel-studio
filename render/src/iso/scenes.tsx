import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Scene, Theme, Style } from "../types";
import { fadeIn } from "../motion";
import { fontFamily } from "../fonts";
import { SCALE, titleSize } from "../scale";
import { fitFontSize } from "../text-fit";
import { IsoSlab, isoOffset } from "./IsoSlab";

type Props = { scene: Scene; theme: Theme; style: Style };

const MARGIN = 80;
const DEPTH = 40;

const palette = (theme: Theme, style: Style): string[] => [
  ...(style.look.palette ?? []),
  theme.colors.accent,
];
const ink = (theme: Theme, style: Style): string => style.look.ink ?? theme.colors.text;

/** Entrada de cada placa: sobe e aparece, em sequência. */
const enter = (frame: number, index: number, perItem: number) => {
  const p = fadeIn(frame, index * perItem, index * perItem + 10);
  return { opacity: p, lift: (1 - p) * 40 };
};

const label = (theme: Theme, style: Style, size: number, weight = 800): React.CSSProperties => ({
  fontFamily: fontFamily(theme.fonts.title), fontWeight: weight, fontSize: size,
  color: ink(theme, style), lineHeight: 1.2,
});

/** `title`, `highlight` e `cta`: a frase numa placa grande flutuante, com placas de apoio. */
export const IsoPhrase: React.FC<Props> = ({ scene, theme, style }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const colors = palette(theme, style);
  const { dx, dy } = isoOffset(DEPTH);
  const text = ("text" in scene && scene.text) || (scene.type === "cta" ? theme.cta.text : "");
  const handle = scene.type === "cta" ? theme.cta.handle : undefined;
  const w = width - 2 * MARGIN - dx;
  const inner = w - 120;
  const size = titleSize(text, inner);
  const lines = Math.ceil((text.length * size * 0.56) / inner);
  const h = Math.max(760, lines * size * 1.2 + 240);
  const bob = Math.sin(frame / 14) * 10;
  const mainY = (height - h - dy) / 2;
  const colorIndex = scene.type === "title" ? 0 : scene.type === "highlight" ? 2 : 1;
  const a = enter(frame, 1, 6);
  const b = enter(frame, 2, 6);
  const main = enter(frame, 0, 6);
  return (
    <>
      <IsoSlab x={MARGIN} y={140} w={520} h={170} color={colors[(colorIndex + 1) % colors.length]}
        depth={DEPTH} opacity={a.opacity} lift={a.lift} />
      <IsoSlab x={MARGIN + 30} y={mainY} w={w - 30} h={h} color={colors[colorIndex % colors.length]}
        depth={DEPTH + 16} opacity={main.opacity} lift={main.lift + bob}>
        <div style={{ ...label(theme, style, size), width: "100%", textAlign: "center", padding: "0 60px" }}>
          {text}
        </div>
      </IsoSlab>
      <IsoSlab x={width - MARGIN - dx - 620} y={height - 140 - 170 - dy} w={620} h={170}
        color={colors[(colorIndex + 2) % colors.length]} depth={DEPTH} opacity={b.opacity} lift={b.lift}>
        {handle && (
          <div style={{ ...label(theme, style, SCALE.secondary, 700), width: "100%", textAlign: "center" }}>
            {handle}
          </div>
        )}
      </IsoSlab>
    </>
  );
};

/** `flow`: placas em escada diagonal pelo quadro, ligadas por setas verticais. */
export const IsoFlow: React.FC<Props> = ({ scene, theme, style }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const steps = scene.type === "flow" ? scene.steps ?? [] : [];
  const colors = palette(theme, style);
  const accent = theme.colors.accent;
  const { dx, dy } = isoOffset(DEPTH);
  const n = Math.max(steps.length, 1);
  const usable = height - 2 * MARGIN;
  const w = 700;
  const h = Math.min(260, (usable * 0.55) / n);
  const pitch = n > 1 ? (usable - h - dy) / (n - 1) : 0;
  const maxShift = width - 2 * MARGIN - dx - w;
  const xAt = (i: number) => MARGIN + (n > 1 ? (i * maxShift) / (n - 1) : maxShift / 2);
  const yAt = (i: number) => MARGIN + dy + (n > 1 ? i * pitch : (usable - h) / 2);
  const perStep = 14;
  const size = Math.min(SCALE.body, ...steps.map((st) => fitFontSize(st, w - 260, SCALE.body, SCALE.secondary)));
  return (
    <>
      {steps.map((step, i) => {
        const e = enter(frame, i, perStep);
        return (
          <React.Fragment key={i}>
            <IsoSlab x={xAt(i)} y={yAt(i)} w={w} h={h} color={colors[i % (colors.length - 1)]}
              depth={DEPTH} opacity={e.opacity} lift={e.lift}>
              <div style={{ display: "flex", alignItems: "center", gap: 28, padding: "0 36px", width: "100%" }}>
                <span style={{
                  ...label(theme, style, SCALE.min), flex: "none", width: 80, height: 80, borderRadius: "50%",
                  background: accent, display: "flex", alignItems: "center", justifyContent: "center",
                }}>{i + 1}</span>
                <span style={label(theme, style, size)}>{step}</span>
              </div>
            </IsoSlab>
            {i < steps.length - 1 && (
              <svg width={width} height={height} style={{
                position: "absolute", left: 0, top: 0, opacity: enter(frame, i + 1, perStep).opacity,
              }}>
                <Arrow x={xAt(i + 1) + 140} y1={yAt(i) + h + dy + 14} y2={yAt(i + 1) - 14} color={accent} />
              </svg>
            )}
          </React.Fragment>
        );
      })}
    </>
  );
};

const Arrow: React.FC<{ x: number; y1: number; y2: number; color: string }> = ({ x, y1, y2, color }) => (
  <>
    <line x1={x} y1={y1} x2={x} y2={y2 - 24} stroke={color} strokeWidth={10} strokeLinecap="round" />
    <polygon points={`${x - 24},${y2 - 30} ${x + 24},${y2 - 30} ${x},${y2}`} fill={color} />
  </>
);

/** `list`: itens em placas empilhadas e levemente deslocadas. */
export const IsoList: React.FC<Props> = ({ scene, theme, style }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const items = scene.type === "list" ? scene.items ?? [] : [];
  const colors = palette(theme, style);
  const { dx, dy } = isoOffset(DEPTH);
  const n = Math.max(items.length, 1);
  const gap = 56;
  const h = Math.min(480, (height - 2 * MARGIN - dy * n - (n - 1) * gap) / n);
  const total = n * (h + dy) + (n - 1) * gap;
  const top = (height - total) / 2 + dy;
  const w = width - 2 * MARGIN - dx - 60;
  return (
    <>
      {items.map((item, i) => {
        const e = enter(frame, i, 12);
        const size = fitFontSize(item, w - 140, SCALE.body, SCALE.secondary);
        return (
          <IsoSlab key={i} x={MARGIN + (i % 2) * 60} y={top + i * (h + dy + gap)} w={w} h={h}
            color={colors[i % (colors.length - 1)]} depth={DEPTH} opacity={e.opacity} lift={e.lift}>
            <div style={{ ...label(theme, style, size, 700), padding: "0 60px", width: "100%" }}>{item}</div>
          </IsoSlab>
        );
      })}
    </>
  );
};

/** `compare`: duas placas lado a lado, com o rótulo e os pontos de cada lado. */
export const IsoCompare: React.FC<Props> = ({ scene, theme, style }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const colors = palette(theme, style);
  const { dx, dy } = isoOffset(DEPTH);
  const sides = scene.type === "compare" ? [scene.left, scene.right] : [];
  const gap = 40;
  const w = (width - 2 * MARGIN - gap - 2 * dx) / 2;
  const h = 1200;
  const top = enter(frame, 2, 10);
  return (
    <>
      <IsoSlab x={MARGIN} y={140} w={420} h={110} color={colors[colors.length - 1]} depth={DEPTH}
        opacity={top.opacity} lift={top.lift} />
      <IsoSlab x={width - MARGIN - dx - 420} y={height - 140 - 110 - dy} w={420} h={110} color={colors[2]}
        depth={DEPTH} opacity={top.opacity} lift={top.lift} />
      {sides.map((side, i) => {
        const e = enter(frame, i, 10);
        return (
          <IsoSlab key={i} x={MARGIN + i * (w + dx + gap)} y={(height - h - dy) / 2} w={w} h={h}
            color={colors[i % (colors.length - 1)]} depth={DEPTH} opacity={e.opacity} lift={e.lift}>
            <div style={{ width: "100%", height: "100%", padding: 36, boxSizing: "border-box", overflow: "hidden" }}>
              <div style={{ ...label(theme, style, SCALE.secondary), marginBottom: 32 }}>{side?.label ?? ""}</div>
              {(side?.points ?? []).map((p, j) => (
                <div key={j} style={{ ...label(theme, style, SCALE.min, 500), marginBottom: 28 }}>{p}</div>
              ))}
            </div>
          </IsoSlab>
        );
      })}
    </>
  );
};
