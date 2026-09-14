/** @type {import('tailwindcss').Config} */
function withOpacity(variable) {
  return `rgb(var(${variable}) / <alpha-value>)`;
}

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Manrope", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        canvas: withOpacity("--color-canvas"),
        surface: {
          DEFAULT: withOpacity("--color-surface"),
          subtle: withOpacity("--color-surface-subtle"),
        },
        ink: {
          DEFAULT: withOpacity("--color-ink"),
          secondary: withOpacity("--color-ink-secondary"),
          faint: withOpacity("--color-ink-faint"),
        },
        line: {
          DEFAULT: withOpacity("--color-line"),
          strong: withOpacity("--color-line-strong"),
        },
        edge: {
          positive: withOpacity("--color-positive"),
          "positive-soft": withOpacity("--color-positive-soft"),
          negative: withOpacity("--color-negative"),
          "negative-soft": withOpacity("--color-negative-soft"),
          warning: withOpacity("--color-warning"),
          "warning-soft": withOpacity("--color-warning-soft"),
          info: withOpacity("--color-info"),
          "info-soft": withOpacity("--color-info-soft"),
        },

        // shadcn-style aliases — every one of these is just a semantic name
        // for a token already defined above, so dark mode support is free.
        border: withOpacity("--color-line"),
        input: withOpacity("--color-line"),
        ring: withOpacity("--color-primary"),
        background: withOpacity("--color-canvas"),
        foreground: withOpacity("--color-ink"),
        primary: {
          DEFAULT: withOpacity("--color-primary"),
          foreground: withOpacity("--color-primary-foreground"),
        },
        secondary: {
          DEFAULT: withOpacity("--color-surface-subtle"),
          foreground: withOpacity("--color-ink"),
        },
        muted: {
          DEFAULT: withOpacity("--color-surface-subtle"),
          foreground: withOpacity("--color-ink-secondary"),
        },
        accent: {
          DEFAULT: withOpacity("--color-surface-subtle"),
          foreground: withOpacity("--color-ink"),
        },
        destructive: {
          DEFAULT: withOpacity("--color-negative"),
          foreground: withOpacity("--color-primary-foreground"),
        },
        popover: {
          DEFAULT: withOpacity("--color-canvas"),
          foreground: withOpacity("--color-ink"),
        },
        card: {
          DEFAULT: withOpacity("--color-canvas"),
          foreground: withOpacity("--color-ink"),
        },
      },
      borderRadius: {
        lg: "12px",
        md: "10px",
        sm: "8px",
        xl: "16px",
      },
      boxShadow: {
        subtle: "0 1px 2px rgba(0, 0, 0, 0.05)",
        panel: "0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.05)",
        elevated: "0 8px 24px rgba(0, 0, 0, 0.16)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        "slide-up": {
          from: { opacity: 0, transform: "translateY(6px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
        "signal-pulse": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.55 },
        },
        shimmer: {
          "0%": { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out",
        "slide-up": "slide-up 0.3s ease-out",
        "signal-pulse": "signal-pulse 2s ease-in-out infinite",
        shimmer: "shimmer 1.6s linear infinite",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
