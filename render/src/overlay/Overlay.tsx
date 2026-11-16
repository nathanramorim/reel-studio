import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { OverlayItem, OverlayProps, Style, Theme } from "../types";
import { useThemeFonts, fontFamily } from "../fonts";
import { Probe } from "../probe";
import { SCALE, titleSize } from "../scale";
import { springForge } from "../motion";
import { Card } from "../forge/Card";
import { Chip } from "../forge/Chip";
import { GradText } from "../forge/GradText";
import { monoFont, panelSpec } from "../forge/panel";
import { OVERLAY_FADE_SECONDS, REGIONS, SIDE } from "./regions";

const WIDTH = 1080;
const CONTENT_W = WIDTH - 2 * SIDE;
const LOGO_BOX = 120;
const BAR_H = 10;
const STRIP_TYPES = ["keyword", "step", "callout"];

/** Visibilidade 0..1 do item no quadro: entrada em mola e saída em fade, função só do quadro. */
const presence = (o: OverlayItem, frame: number, fps: number): number => {
  const start = o.at * fps;
  const end = (o.at + o.dur) * fps;
  if (frame < start || frame >= end) return 0;
  const fade = OVERLAY_FADE_SECONDS * fps;
  const out = Math.min(1, (end - frame) / fade);
  return Math.min(1, springForge(frame, fps, start)) * out;
};

const accentAt = (style: Style, theme: Theme, i: number): string => {
  const palette = style.look.palette?.length ? style.look.palette : [theme.colors.accent];
  return palette[i % palette.length];
};

const Frame: React.FC<{ theme: Theme; accent: string }> = ({ theme, accent }) => {
  const spec = panelSpec(theme);
  const dots = [theme.colors.bad ?? accent, theme.colors.warn ?? accent, theme.colors.success ?? accent];
  return (
    <div style={{
      position: "absolute", left: 40, width: WIDTH - 80, top: REGIONS.frame.top, height: REGIONS.frame.height,
      border: `3px solid ${spec.border}`, borderRadius: spec.radius,
    }}>
      {spec.bar && dots.slice(0, spec.dots).map((c, i) => (
        <div key={i} style={{
          position: "absolute", top: -9, left: 28 + i * 28, width: 14, height: 14, borderRadius: "50%", background: c,
        }} />
      ))}
    </div>
  );
};

export const Overlay: React.FC<OverlayProps> = ({ overlays, theme, style, fps, probe }) => {
  useThemeFonts(theme);
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const ink = style.look.ink ?? theme.colors.bg;
  const logoUri = theme.brand?.logoUri;
  const active = overlays.map((o, i) => ({ o, i, p: presence(o, frame, fps) })).filter((a) => a.p > 0);
  const strip = active.filter((a) => STRIP_TYPES.includes(a.o.type));
  const families = [...new Set([theme.fonts.title, theme.fonts.body, monoFont(theme)])].filter((f): f is string => !!f);
  const hasLogo = active.some((a) => a.o.type === "logo");
  return (
    <AbsoluteFill id="probe-root">
      {probe && <Probe families={families} />}
      {overlays.length > 0 && <Frame theme={theme} accent={accentAt(style, theme, 0)} />}
      {active.map(({ o, i, p }) => {
        const accent = accentAt(style, theme, i);
        if (o.type === "hook") {
          const text = o.text ?? "";
          return (
            <div key={i} style={{
              position: "absolute", left: SIDE, width: CONTENT_W - (hasLogo ? LOGO_BOX + 20 : 0),
              top: REGIONS.hook.top, height: REGIONS.hook.height,
              display: "flex", alignItems: "center", opacity: p,
            }}>
              <Card theme={theme} accent={accent} style={{ width: "100%", textAlign: "center", padding: "20px 24px" }}>
                <div style={{
                  fontFamily: fontFamily(theme.fonts.title), fontWeight: 800, lineHeight: 1.15,
                  fontSize: titleSize(text, CONTENT_W - (hasLogo ? LOGO_BOX + 20 : 0) - 48),
                }}>
                  <GradText theme={theme}>{text}</GradText>
                </div>
              </Card>
            </div>
          );
        }
        if (STRIP_TYPES.includes(o.type)) {
          const slot = strip.findIndex((a) => a.i === i);
          const top = REGIONS.strip.bottom - (slot + 1) * REGIONS.strip.slot;
          return (
            <div key={i} style={{
              position: "absolute", left: SIDE, width: CONTENT_W, top, height: REGIONS.strip.slot - 12,
              display: "flex", alignItems: "center", justifyContent: "center", opacity: p,
              transform: `translateY(${(1 - p) * 24}px)`,
            }}>
              {o.type === "callout" ? (
                <Card theme={theme} accent={accent} style={{ padding: "10px 28px", textAlign: "center" }}>
                  <div style={{ fontFamily: fontFamily(theme.fonts.body), fontWeight: 700, fontSize: SCALE.secondary, color: theme.colors.text }}>
                    {o.text ?? ""}
                  </div>
                </Card>
              ) : (
                <Chip theme={theme} fill={accent} ink={ink}>
                  {o.type === "step" ? `${strip.filter((a) => a.o.type === "step" && a.i <= i).length}  ` : ""}{o.text ?? ""}
                </Chip>
              )}
            </div>
          );
        }
        if (o.type === "progress") {
          return (
            <div key={i} style={{
              position: "absolute", left: SIDE, width: CONTENT_W, top: REGIONS.footer.top, height: BAR_H,
              borderRadius: BAR_H, background: theme.colors.surface, opacity: p,
            }}>
              <div style={{
                width: `${Math.min(1, frame / Math.max(1, durationInFrames)) * 100}%`, height: "100%",
                borderRadius: BAR_H, background: accent,
              }} />
            </div>
          );
        }
        if (o.type === "cta") {
          return (
            <div key={i} style={{
              position: "absolute", left: SIDE, right: SIDE,
              top: REGIONS.footer.top + 16, height: REGIONS.footer.height - 16, display: "flex",
              alignItems: "center", opacity: p,
            }}>
              <Card theme={theme} accent={accent} style={{ width: "100%", padding: "6px 24px" }}>
                <div style={{
                  fontFamily: fontFamily(monoFont(theme)), fontWeight: 500, fontSize: SCALE.min,
                  color: theme.colors.text, lineHeight: 1.2, overflowWrap: "anywhere",
                }}>
                  {o.text ?? theme.cta.text}
                </div>
              </Card>
            </div>
          );
        }
        if (o.type === "logo" && logoUri) {
          return (
            <img key={i} src={logoUri} style={{
              position: "absolute", left: SIDE + CONTENT_W - (LOGO_BOX - 20), top: REGIONS.hook.top + 20,
              width: LOGO_BOX - 20, height: LOGO_BOX - 20,
              objectFit: "contain", opacity: p,
            }} />
          );
        }
        return null;
      })}
    </AbsoluteFill>
  );
};
