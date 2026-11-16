import { Theme } from "../types";

/** Cor de token do tema (ou hex) com recuo no `muted` (ADR-0001: o estilo não tem cor própria). */
export const themeColor = (theme: Theme, token: string | undefined, fallback: string): string => {
  if (!token) return fallback;
  if (token.startsWith("#")) return token;
  const colors = theme.colors as Record<string, string | string[] | undefined>;
  const value = colors[token];
  return typeof value === "string" ? value : fallback;
};

/** Valores do painel com os padrões do `brand` (tema sem `brand` continua renderizando). */
export const panelSpec = (theme: Theme) => {
  const p = theme.brand?.panel ?? {};
  return {
    radius: p.radius ?? 18,
    border: themeColor(theme, p.border, theme.colors.muted),
    bar: p.bar ?? true,
    dots: p.dots ?? 3,
  };
};

export const packetSpec = (theme: Theme) => ({
  glow: theme.brand?.packet?.glow ?? true,
  radius: theme.brand?.packet?.radius ?? 999,
});

/** Fonte mono do tema: `brand.mono`, depois `fonts.mono`. */
export const monoFont = (theme: Theme): string | undefined => theme.brand?.mono ?? theme.fonts.mono;

/** Degradê do tema; sem `gradient`, cai em accent e accent2. */
export const gradientStops = (theme: Theme): string[] =>
  theme.colors.gradient?.length ? theme.colors.gradient : [theme.colors.accent, theme.colors.accent2 ?? theme.colors.accent];
