import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Scene, Theme, Style, Word } from "../types";
import { fontFamily } from "../fonts";
import { SCALE, titleSize } from "../scale";
import { CAMERA_MARGIN, SAFE, SIDE_MARGIN } from "../safeZone";
import { CAPTION } from "../overlay/regions";
import { fitFontSize } from "../text-fit";
import { easeOut, springForge, stagger } from "../motion";
import { Camera } from "./Camera";
import { Card } from "./Card";
import { Chip } from "./Chip";
import { GradWords, startOf } from "./GradText";
import { Packet } from "./Packet";
import { Pane } from "./Pane";
import { monoFont } from "./panel";

type Props = { scene: Scene; theme: Theme; style: Style };

const WIDTH = 1080;
const CONTENT_W = WIDTH - 2 * SIDE_MARGIN;
const AREA_TOP = SAFE.top + CAMERA_MARGIN;
/** Folga mínima entre o conteúdo e a legenda (`CAPTION`, DUP-03): o conteúdo termina acima dela. */
const CAPTION_GAP = 40;
const AREA_H = CAPTION.top - CAPTION_GAP - SAFE.top - 2 * CAMERA_MARGIN;
const GAP = 28;
const PACKET_SECONDS = 1.2;
const STEP = 0.18;
const BALANCE: React.CSSProperties = { textWrap: "balance" } as React.CSSProperties;
const FILL: React.CSSProperties = { display: "flex", flexDirection: "column", justifyContent: "center" };

const accents = (theme: Theme, style: Style): string[] =>
  style.look.palette?.length ? style.look.palette : [theme.colors.accent];
const pick = (list: string[], i: number): string => list[i % list.length];
const inkOf = (theme: Theme, style: Style): string => style.look.ink ?? theme.colors.bg;

/** Palco da cena: câmera e área de conteúdo dentro da zona segura. */
const Stage: React.FC<{ children: React.ReactNode; align?: "center" | "stretch" }> = ({
  children, align = "center",
}) => (
  <Camera>
    <div style={{
      position: "absolute", left: SIDE_MARGIN, width: CONTENT_W, top: AREA_TOP, height: AREA_H,
      display: "flex", flexDirection: "column", justifyContent: align === "center" ? "center" : "stretch",
      gap: GAP,
    }}>
      {children}
    </div>
  </Camera>
);

/** Entrada da unidade `i` de `n`: no tempo da fala (`words`), ou escalonada sem tempos. */
const useEnter = (i: number, words?: Word[], n = 1) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const at = startOf(words, i, n, i * STEP);
  return { enter: Math.min(1, springForge(frame, fps, Math.round(at * fps))), at };
};

const body = (theme: Theme): React.CSSProperties => ({
  fontFamily: fontFamily(theme.fonts.body), color: theme.colors.text, fontWeight: 700,
});

/** Texto com termos entre crases em mono (chips de termos técnicos). */
const Inline: React.FC<{ text: string; theme: Theme }> = ({ text, theme }) => (
  <>
    {text.split("`").map((part, i) => i % 2 === 1
      ? <span key={i} style={{ fontFamily: fontFamily(monoFont(theme)), fontWeight: 500 }}>{part}</span>
      : <React.Fragment key={i}>{part}</React.Fragment>)}
  </>
);

export const ForgePhrase: React.FC<Props> = ({ scene, theme, style }) => {
  const text = "text" in scene ? scene.text ?? "" : "";
  const { enter } = useEnter(0);
  const [a] = accents(theme, style);
  return (
    <Stage>
      <Card theme={theme} accent={a} opacity={enter} offsetX={(1 - enter) * -40}
        style={{ ...FILL, padding: "48px 40px", textAlign: "center", minHeight: AREA_H * 0.88 }}>
        <div style={{ ...body(theme), fontWeight: 800, fontSize: titleSize(text, CONTENT_W - 80), lineHeight: 1.15 }}>
          <GradWords theme={theme} text={text} words={scene.words} fallbackStep={0.12} />
        </div>
      </Card>
    </Stage>
  );
};

export const ForgeFlow: React.FC<Props> = ({ scene, theme, style }) => {
  const steps = scene.type === "flow" ? scene.steps ?? [] : [];
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const list = accents(theme, style);
  const count = Math.max(steps.length, 1);
  const paneH = Math.min(260, (AREA_H - GAP * (count - 1)) / count);
  const total = paneH * count + GAP * (count - 1);
  const top = AREA_TOP + (AREA_H - total) / 2;
  const x = SIDE_MARGIN + CONTENT_W / 2;
  const period = Math.round(PACKET_SECONDS * fps);
  return (
    <Camera>
      <div style={{ position: "absolute", inset: 0 }}>
        <div style={{
          position: "absolute", left: SIDE_MARGIN, width: CONTENT_W, top, display: "flex",
          flexDirection: "column", gap: GAP,
        }}>
          {steps.map((step, i) => {
            const at = startOf(scene.words, i, steps.length, i * 0.3);
            const enter = Math.min(1, springForge(frame, fps, Math.round(at * fps)));
            return (
              <Pane key={i} theme={theme} accent={pick(list, i)} opacity={enter} reveal={at}
                style={{ height: paneH, transform: `translateY(${(1 - enter) * 30}px)` }}>
                <div style={{
                  ...body(theme), whiteSpace: "nowrap",
                  fontSize: fitFontSize(`${i + 1} ${step.split("`").join("")}`, CONTENT_W - 60, SCALE.body, SCALE.min),
                }}>
                  <span style={{ color: pick(list, i), fontFamily: fontFamily(monoFont(theme)) }}>{i + 1}</span>{" "}
                  <Inline text={step} theme={theme} />
                </div>
              </Pane>
            );
          })}
        </div>
        {steps.slice(0, -1).map((_, i) => {
          const start = stagger(i + 1, fps, 0.3) + period * 0.5;
          const progress = easeOut(((frame - start) % period) / period);
          const from = top + (i + 1) * paneH + i * GAP;
          return (
            <Packet key={i} theme={theme} color={pick(list, i)} x={x} from={from} to={from + GAP}
              progress={frame >= start ? progress : 0} />
          );
        })}
      </div>
    </Camera>
  );
};

export const ForgeList: React.FC<Props> = ({ scene, theme, style }) => {
  const items = scene.type === "list" ? scene.items ?? [] : [];
  const list = accents(theme, style);
  const Item: React.FC<{ item: string; i: number }> = ({ item, i }) => {
    const { enter, at } = useEnter(i, scene.words, items.length);
    return (
      <Card theme={theme} accent={pick(list, i)} opacity={enter} offsetX={(1 - enter) * -60} reveal={at}
        style={{ ...FILL, flex: "1 1 0", maxHeight: 360 }}>
        <div style={{ ...body(theme), fontSize: SCALE.body }}><Inline text={item} theme={theme} /></div>
      </Card>
    );
  };
  return (
    <Stage>
      {items.map((item, i) => <Item key={i} item={item} i={i} />)}
    </Stage>
  );
};

export const ForgeCompare: React.FC<Props> = ({ scene, theme, style }) => {
  const sides = scene.type === "compare" ? [scene.left, scene.right] : [];
  const list = accents(theme, style);
  const Side: React.FC<{ i: number }> = ({ i }) => {
    const { enter } = useEnter(i * 2);
    const side = sides[i];
    return (
      <Pane theme={theme} accent={pick(list, i)} opacity={enter} style={{ flex: 1, transform: `translateY(${(1 - enter) * 30}px)` }}>
        <div style={{ ...body(theme), fontWeight: 800, fontSize: SCALE.body, color: pick(list, i), marginBottom: 16 }}>
          {side?.label ?? ""}
        </div>
        {(side?.points ?? []).map((p, k) => (
          <div key={k} style={{ ...body(theme), fontWeight: 500, fontSize: SCALE.secondary, marginBottom: 12 }}>
            <Inline text={p} theme={theme} />
          </div>
        ))}
      </Pane>
    );
  };
  return (
    <Stage align="stretch">
      <Side i={0} />
      <Side i={1} />
    </Stage>
  );
};

export const ForgeCta: React.FC<Props> = ({ scene, theme, style }) => {
  const text = scene.type === "cta" ? scene.text ?? theme.cta.text : theme.cta.text;
  const { enter } = useEnter(0);
  const [a, b] = accents(theme, style);
  return (
    <Stage>
      <Pane theme={theme} accent={a} opacity={enter} style={{ ...FILL, padding: "60px 0", flex: "1 1 0", maxHeight: 700 }}>
        <div data-cta="" style={{ ...BALANCE, padding: "0 32px",
          fontFamily: fontFamily(monoFont(theme)), fontWeight: 500, fontSize: SCALE.body,
          color: theme.colors.text, textAlign: "center", lineHeight: 1.3,
        }}>
          <span style={{ color: b ?? a }}>$ </span>{text}
        </div>
      </Pane>
      {theme.cta.handle && (
        <div style={{ textAlign: "center", opacity: enter }}>
          <Chip theme={theme} fill={a} ink={inkOf(theme, style)}>{theme.cta.handle}</Chip>
        </div>
      )}
    </Stage>
  );
};
