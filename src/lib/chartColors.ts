/**
 * Recharts and raw SVG need real color values at render time — they can't
 * read Tailwind's `dark:` variant or resolve CSS custom properties the way
 * className-based elements can. This is the single place those literal
 * values live, kept in lockstep with the CSS variables in src/index.css.
 */
export interface ChartPalette {
  positive: string;
  negative: string;
  warning: string;
  info: string;
  ink: string;
  inkSecondary: string;
  inkFaint: string;
  line: string;
  lineStrong: string;
  surfaceSubtle: string;
  canvas: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
}

const LIGHT: ChartPalette = {
  positive: "#16845B",
  negative: "#D64545",
  warning: "#B7791F",
  info: "#356AE6",
  ink: "#111318",
  inkSecondary: "#667085",
  inkFaint: "#98A2B3",
  line: "#E6E8EC",
  lineStrong: "#D0D5DD",
  surfaceSubtle: "#F4F5F7",
  canvas: "#FFFFFF",
  tooltipBg: "#FFFFFF",
  tooltipBorder: "#E6E8EC",
  tooltipText: "#111318",
};

const DARK: ChartPalette = {
  positive: "#30A46C",
  negative: "#E5484D",
  warning: "#E0A83E",
  info: "#5E97F6",
  ink: "#EDEEF0",
  inkSecondary: "#949DAB",
  inkFaint: "#646C7A",
  line: "#282C32",
  lineStrong: "#383D45",
  surfaceSubtle: "#181B1F",
  canvas: "#0A0B0D",
  tooltipBg: "#121417",
  tooltipBorder: "#282C32",
  tooltipText: "#EDEEF0",
};

export function getChartPalette(theme: "light" | "dark"): ChartPalette {
  return theme === "dark" ? DARK : LIGHT;
}
