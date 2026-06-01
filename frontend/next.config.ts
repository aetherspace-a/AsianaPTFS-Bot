import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  outputFileTracingRoot: path.join(__dirname, ".."),
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/assets/**",
      },
      {
        protocol: "http",
        hostname: "api",
        pathname: "/assets/**",
      },
    ],
  },
};

export default nextConfig;
