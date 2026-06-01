import type { Config } from "tailwindcss";
import branding from "../branding.json";

const colors = branding.colors;

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: colors.primary,
          secondary: colors.secondary,
          accent: colors.accent,
          background: colors.background,
          surface: colors.surface,
          text: colors.text,
          muted: colors.text_muted,
          success: colors.success,
          warning: colors.warning,
          error: colors.error,
        },
      },
    },
  },
  plugins: [],
};

export default config;
