import branding from "../../../branding.json";

export type Branding = typeof branding;

export function getBranding(): Branding {
  return branding;
}

export const brandingConfig = getBranding();
