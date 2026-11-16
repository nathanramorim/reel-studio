import { fitFontSize } from "./text-fit";

/** Escala tipográfica única para o quadro 1080×1920 (DUP-03): nenhuma cena usa número solto. */
export const SCALE = {
  titleMax: 120,
  titleMin: 72,
  body: 64,
  secondary: 48,
  min: 44,
} as const;

/** Título: 120 a 72 px conforme o comprimento do texto e a largura disponível. */
export const titleSize = (text: string, maxWidth: number): number =>
  fitFontSize(text, maxWidth, SCALE.titleMax, SCALE.titleMin);
