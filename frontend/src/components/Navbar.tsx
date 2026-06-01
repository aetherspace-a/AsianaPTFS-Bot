"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { brandingConfig } from "@/lib/branding";
import { API_URL } from "@/lib/api";
import { clearToken, isLoggedIn } from "@/lib/auth";
import { BrandLogo } from "@/components/BrandLogo";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/flights", label: "Flights" },
  { href: "/tracker", label: "Live Tracker" },
  { href: "/leaderboard", label: "Leaderboard" },
  { href: "/admin", label: "Admin" },
];

export function Navbar() {
  const pathname = usePathname();
  const loggedIn = isLoggedIn();

  return (
    <header className="border-b border-white/10 bg-brand-surface/80 backdrop-blur sticky top-0 z-50">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <BrandLogo variant="icon" width={36} height={36} className="rounded-full" />
          <span>{brandingConfig.airline_name}</span>
        </Link>
        <nav className="hidden items-center gap-6 md:flex">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={
                pathname.startsWith(l.href)
                  ? "text-brand-accent"
                  : "text-brand-muted hover:text-brand-text"
              }
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          {loggedIn ? (
            <button
              type="button"
              onClick={() => {
                clearToken();
                window.location.href = "/";
              }}
              className="rounded-lg border border-white/20 px-3 py-1.5 text-sm hover:bg-white/5"
            >
              Log out
            </button>
          ) : (
            <a
              href={`${API_URL}/api/auth/discord`}
              className="rounded-lg bg-brand-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90"
            >
              Login with Discord
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
