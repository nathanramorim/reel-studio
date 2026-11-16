import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Theme, Word } from "../types";
import { fontFamily } from "../fonts";
import { gradientStops, monoFont } from "./panel";

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

const REVEAL_SECONDS = 0.14;

/** Opacidade de revelação de quem aparece em `at` (s): função só do quadro (sem estado entre quadros). */
export const revealAt = (frame: number, fps: number, at: number): number =>
  Math.min(1, Math.max(0, (frame / fps - at) / REVEAL_SECONDS));

/** Quando a unidade `i` de `n` (palavra ou item) aparece: no tempo da fala, ou `fallback` sem tempos. */
export const startOf = (words: Word[] | undefined, i: number, n: number, fallback: number): number =>
  words?.length ? words[Math.min(words.length - 1, Math.floor((i * words.length) / Math.max(n, 1)))].start : fallback;

/** Texto em degradê revelado palavra a palavra no tempo da fala; termos entre crases saem em mono. */
export const GradWords: React.FC<{ theme: Theme; text: string; words?: Word[]; fallbackStep?: number }> = ({
  theme, text, words, fallbackStep = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const mono = monoFont(theme);
  const tokens = text.split("`").flatMap((part, k) =>
    part.split(/\s+/).filter(Boolean).map((token) => ({ token, code: k % 2 === 1 })));
  return (
    <>
      {tokens.map(({ token, code }, i) => {
        const at = startOf(words, i, tokens.length, i * fallbackStep);
        return (
          <React.Fragment key={i}>
            {i > 0 && " "}
            <span data-reveal-at={at} style={{
              backgroundImage: `linear-gradient(90deg, ${gradientStops(theme).join(", ")})`,
              WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
              WebkitTextFillColor: "transparent", opacity: revealAt(frame, fps, at),
              fontFamily: code && mono ? fontFamily(mono) : undefined, fontWeight: code ? 500 : undefined,
            }}>
              {token}
            </span>
          </React.Fragment>
        );
      })}
    </>
  );
};
