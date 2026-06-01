"use client";

import Image from "next/image";
import { useState } from "react";
import { getLogoSrc, PLACEHOLDER_LOGO, resolveAssetUrl, type LogoVariant } from "@/lib/assets";

interface BrandLogoProps {
  variant?: LogoVariant;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
}

export function BrandLogo({
  variant = "icon",
  width = 36,
  height = 36,
  className = "",
  priority = false,
}: BrandLogoProps) {
  const primary = resolveAssetUrl(getLogoSrc(variant));
  const fallback = PLACEHOLDER_LOGO;
  const [src, setSrc] = useState(primary);

  return (
    <Image
      src={src}
      alt="Airline logo"
      width={width}
      height={height}
      className={className}
      priority={priority}
      onError={() => {
        if (src !== fallback) setSrc(fallback);
      }}
    />
  );
}
