"use client";

import Image from "next/image";
import { useState } from "react";
import { brandingConfig } from "@/lib/branding";
import { getLogoSrc, PLACEHOLDER_LOGO, resolveAssetUrl } from "@/lib/assets";

export function HomeBanner() {
  const [src, setSrc] = useState(resolveAssetUrl(getLogoSrc("banner")));

  return (
    <div className="relative h-48 overflow-hidden rounded-2xl border border-white/10 md:h-64">
      <Image
        src={src}
        alt={`${brandingConfig.airline_name} banner`}
        fill
        className="object-cover"
        priority
        onError={() => {
          if (src !== PLACEHOLDER_LOGO) setSrc(PLACEHOLDER_LOGO);
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-brand-background/90 to-transparent" />
    </div>
  );
}
