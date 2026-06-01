import { brandingConfig } from "./branding";

export const PLACEHOLDER_LOGO = "/assets/logos/placeholder.svg";

export type LogoVariant = "main" | "icon" | "banner";

const logos = brandingConfig.logos;

export function getLogoSrc(variant: LogoVariant = "icon"): string {
  const map = {
    main: logos.main,
    icon: logos.icon,
    banner: logos.banner,
  };
  return map[variant] || PLACEHOLDER_LOGO;
}

/** Resolve logo URL for Next/Image or img (supports API-hosted assets in production). */
export function resolveAssetUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const api = process.env.NEXT_PUBLIC_API_URL;
  if (api && path.startsWith("/assets/")) {
    return `${api.replace(/\/$/, "")}${path}`;
  }
  return path;
}
