import Link from "next/link";
import { brandingConfig } from "@/lib/branding";
import { API_URL } from "@/lib/api";
import { HomeBanner } from "@/components/HomeBanner";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <HomeBanner />
      <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-brand-secondary to-brand-background p-10 md:p-16">
      <p className="text-sm uppercase tracking-widest text-brand-accent">{brandingConfig.airline_icao}</p>
      <h1 className="mt-2 text-4xl font-bold md:text-5xl">{brandingConfig.airline_name}</h1>
      <p className="mt-4 max-w-xl text-lg text-brand-muted">{brandingConfig.tagline}</p>
      <div className="mt-8 flex flex-wrap gap-4">
        <a
          href={`${API_URL}/api/auth/discord`}
          className="rounded-lg bg-brand-primary px-6 py-3 font-medium text-white hover:opacity-90"
        >
          Get started with Discord
        </a>
        <Link
          href="/flights"
          className="rounded-lg border border-white/20 px-6 py-3 hover:bg-white/5"
        >
          Browse flights
        </Link>
      </div>
    </div>
    </div>
  );
}
