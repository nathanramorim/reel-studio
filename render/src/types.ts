export type Theme = {
  id: string;
  name: string;
  colors: {
    bg: string; surface: string; text: string; muted: string;
    accent: string; accent2?: string; success?: string; warn?: string; bad?: string;
    glow?: string; gradient?: string[];
  };
  fonts: { title: string; body: string; mono?: string };
  caption: { style: "word-highlight" | "line"; position: string; size?: number; uppercase?: boolean };
  logo: string | null;
  brand?: Brand;
  cta: { text: string; handle?: string };
};

/** Kit da marca (contracts/theme.schema.json); `logoUri` e `mascotUri` são data URIs do SVG, lidos pelo motor. */
export type Brand = {
  logo?: string | null; mascot?: string | null; mono?: string;
  logoUri?: string; mascotUri?: string;
  panel?: { radius?: number; border?: string; bar?: boolean; dots?: number };
  packet?: { glow?: boolean; radius?: number };
};

export type Style = {
  id: string;
  name: string;
  renderer: "remotion" | "manim";
  background: "theme" | "own";
  look: { bg?: string; ink?: string; stroke?: string; palette?: string[]; font?: string; motion?: string };
  scene_types: string[];
};

/** Palavra da fala com tempo em segundos, relativo ao início da cena. */
export type Word = { word: string; start: number; end: number };
export type Transition = "cut" | "dip" | "wipe" | "slide";
/** Trecho real da gravação (arquivo no `--public-dir`) e recorte normalizado da região de atividade. */
export type Media = { file: string; start: number; end: number; region: { x: number; y: number; w: number; h: number } };

export type Scene =
  | { type: "title"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; text?: string }
  | { type: "highlight"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; text?: string }
  | { type: "quote"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; text?: string }
  | { type: "flow"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; steps?: string[] }
  | { type: "list"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; items?: string[] }
  | { type: "compare"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; left?: SidePoints; right?: SidePoints }
  | { type: "chart"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; values?: { label: string; value: number }[] }
  | { type: "cta"; dur: number; narration: string; words?: Word[]; transition?: Transition; media?: Media; text?: string };

export type SidePoints = { label: string; points: string[] };

export type ReelProps = {
  scenes: Scene[];
  theme: Theme;
  style: Style;
  fps: number;
  probe?: boolean;
};

export type OverlayItem = {
  at: number; dur: number; text?: string; pos?: "top" | "bottom";
  type: "hook" | "keyword" | "step" | "callout" | "progress" | "cta" | "logo";
};

/** Props da composição `Overlay` (camada transparente sobre o corte); `length` em segundos. */
export type OverlayProps = {
  overlays: OverlayItem[]; theme: Theme; style: Style; fps: number; length: number; probe?: boolean;
  /** Retângulo do vídeo no quadro (core/cut.py `video_rect`); ausente no fill (tela cheia): sem moldura. */
  frame?: { left: number; top: number; width: number; height: number } | null;
};
