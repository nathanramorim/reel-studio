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
  cta: { text: string; handle?: string };
};

export type Style = {
  id: string;
  name: string;
  renderer: "remotion" | "manim";
  background: "theme" | "own";
  look: { bg?: string; ink?: string; stroke?: string; palette?: string[]; font?: string; motion?: string };
  scene_types: string[];
};

export type Scene =
  | { type: "title"; dur: number; narration: string; text?: string }
  | { type: "highlight"; dur: number; narration: string; text?: string }
  | { type: "quote"; dur: number; narration: string; text?: string }
  | { type: "flow"; dur: number; narration: string; steps?: string[] }
  | { type: "list"; dur: number; narration: string; items?: string[] }
  | { type: "compare"; dur: number; narration: string; left?: SidePoints; right?: SidePoints }
  | { type: "chart"; dur: number; narration: string; values?: { label: string; value: number }[] }
  | { type: "cta"; dur: number; narration: string; text?: string };

export type SidePoints = { label: string; points: string[] };

export type ReelProps = {
  scenes: Scene[];
  theme: Theme;
  style: Style;
  fps: number;
  probe?: boolean;
};
