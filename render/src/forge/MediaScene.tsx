import React from "react";
import { OffthreadVideo, staticFile, useVideoConfig } from "remotion";
import { Scene, Theme, Style } from "../types";
import { fontFamily } from "../fonts";
import { SCALE } from "../scale";
import { CAMERA_MARGIN, SAFE, SIDE_MARGIN } from "../safeZone";
import { Camera } from "./Camera";
import { GradWords } from "./GradText";
import { Pane } from "./Pane";

const WIDTH = 1080;
const CONTENT_W = WIDTH - 2 * SIDE_MARGIN;
const AREA_TOP = SAFE.top + CAMERA_MARGIN;
/** Proporção da janela: a mesma da região de atividade do motor (core/frames.BAND_RATIO). */
const ASPECT = 1080 / 920;
const BAR = 44;
const GAP = 28;

const caption = (scene: Scene): string =>
  ("text" in scene && scene.text) || ("steps" in scene && scene.steps?.[0]) || ("items" in scene && scene.items?.[0]) || "";

/** Cena com a gravação real numa janela de terminal, recortada na região de atividade (sem rede). */
export const MediaScene: React.FC<{ scene: Scene; theme: Theme; style: Style }> = ({ scene, theme, style }) => {
  const { fps } = useVideoConfig();
  const media = scene.media;
  if (!media) return null;
  const { region } = media;
  const full = region.w >= 1 && region.h >= 1;
  const bodyW = CONTENT_W - 56;
  const bodyH = Math.round(bodyW / ASPECT);
  const accent = style.look.palette?.[0] ?? theme.colors.accent;
  const text = caption(scene);
  return (
    <Camera>
      <div style={{
        position: "absolute", left: SIDE_MARGIN, width: CONTENT_W, top: AREA_TOP, display: "flex",
        flexDirection: "column", gap: GAP,
      }}>
        <Pane theme={theme} accent={accent} style={{ height: bodyH + BAR + 20 }}>
          <div data-media-box style={{ width: bodyW, height: bodyH, overflow: "hidden", position: "relative", margin: "0 -18px" }}>
            <div style={{
              position: "absolute", width: bodyW / region.w, height: bodyH / region.h,
              left: -(region.x * bodyW) / region.w, top: -(region.y * bodyH) / region.h,
            }}>
              <OffthreadVideo
                src={staticFile(media.file)} startFrom={Math.round(media.start * fps)}
                endAt={Math.round(media.end * fps)} muted
                style={{ width: "100%", height: "100%", objectFit: full ? "contain" : "fill" }}
              />
            </div>
          </div>
        </Pane>
        {text && (
          <div style={{
            fontFamily: fontFamily(theme.fonts.body), fontWeight: 800, fontSize: SCALE.secondary,
            color: theme.colors.text, textAlign: "center", lineHeight: 1.15,
          }}>
            <GradWords theme={theme} text={text} words={scene.words} fallbackStep={0.12} />
          </div>
        )}
      </div>
    </Camera>
  );
};
