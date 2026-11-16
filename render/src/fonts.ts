import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";
import { Theme } from "./types";

type FontFile = { file: string; weight: string };

/** Registro nome da fonte do tema -> arquivos locais em public/fonts (sem rede no render). */
export const FONT_FILES: Record<string, FontFile[]> = {
  Montserrat: [
    { file: "Montserrat-Medium.ttf", weight: "500" },
    { file: "Montserrat-Bold.ttf", weight: "700" },
    { file: "Montserrat-ExtraBold.ttf", weight: "800" },
  ],
  "JetBrains Mono": [{ file: "JetBrainsMono-Medium.ttf", weight: "500" }],
};

const warned = new Set<string>();

/** Pilha CSS da fonte: nome conhecido ou sans-serif com aviso, nunca serifa. */
export const fontFamily = (name: string | undefined): string => {
  if (name && FONT_FILES[name]) return `"${name}", sans-serif`;
  const key = name ?? "(vazio)";
  if (!warned.has(key)) {
    warned.add(key);
    console.warn(`[font-fallback] fonte desconhecida "${key}": usando sans-serif`);
  }
  return "sans-serif";
};

const themeFamilies = (theme: Theme): string[] =>
  [...new Set([theme.fonts.title, theme.fonts.body, theme.fonts.mono])].filter(
    (f): f is string => !!f && !!FONT_FILES[f],
  );

const loadFamily = (family: string) =>
  Promise.all(
    FONT_FILES[family].map(({ file, weight }) =>
      loadFont({ family, url: staticFile(`fonts/${file}`), weight }),
    ),
  );

/** Segura o primeiro quadro até as fontes do tema carregarem. */
export const useThemeFonts = (theme: Theme): void => {
  const [handle] = useState(() => delayRender("fontes do tema"));
  useEffect(() => {
    Promise.all(themeFamilies(theme).map(loadFamily))
      .catch((err) => console.warn(`[font-fallback] falha ao carregar fontes: ${err}`))
      .finally(() => continueRender(handle));
  }, []);
};
