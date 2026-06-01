"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { brandingConfig } from "@/lib/branding";
import type { LeaderboardData } from "@/types";

export default function LeaderboardPage() {
  const [data, setData] = useState<LeaderboardData | null>(null);
  const sym = brandingConfig.economy.currency_symbol;

  useEffect(() => {
    api.get<LeaderboardData>("/api/leaderboard", false).then(setData);
    const interval = setInterval(
      () => api.get<LeaderboardData>("/api/leaderboard", false).then(setData),
      60000,
    );
    return () => clearInterval(interval);
  }, []);

  if (!data) return <p className="text-brand-muted">Loading leaderboards…</p>;

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-bold">Leaderboards</h1>
        <p className="text-brand-muted">
          Top pilots at {brandingConfig.airline_name} · refreshes every minute
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <section className="rounded-xl border border-white/10 bg-brand-surface p-6">
          <h2 className="mb-4 text-xl font-semibold">✈️ Flight hours</h2>
          <ol className="space-y-3">
            {data.top_pilots_by_hours.map((p) => (
              <li
                key={p.discord_id}
                className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3"
              >
                <span className="flex items-center gap-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-primary text-sm font-bold">
                    {p.rank}
                  </span>
                  <span>
                    <span className="font-medium">{p.username}</span>
                    <span className="ml-2 text-xs text-brand-muted">{p.pilot_rank}</span>
                  </span>
                </span>
                <span className="font-semibold text-brand-accent">{p.total_hours}h</span>
              </li>
            ))}
            {data.top_pilots_by_hours.length === 0 && (
              <li className="text-brand-muted">No flight hours logged yet.</li>
            )}
          </ol>
        </section>

        <section className="rounded-xl border border-white/10 bg-brand-surface p-6">
          <h2 className="mb-4 text-xl font-semibold">💰 WON balance</h2>
          <ol className="space-y-3">
            {data.top_pilots_by_wealth.map((p) => (
              <li
                key={p.discord_id}
                className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3"
              >
                <span className="flex items-center gap-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-accent text-sm font-bold text-brand-secondary">
                    {p.rank}
                  </span>
                  <span className="font-medium">{p.username}</span>
                </span>
                <span className="font-semibold">
                  {sym}
                  {p.won_balance.toLocaleString()}
                </span>
              </li>
            ))}
            {data.top_pilots_by_wealth.length === 0 && (
              <li className="text-brand-muted">No pilots yet.</li>
            )}
          </ol>
        </section>
      </div>
    </div>
  );
}
