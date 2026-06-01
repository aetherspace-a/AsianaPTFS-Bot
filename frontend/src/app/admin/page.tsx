"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useStaffGuard } from "@/hooks/useStaffGuard";
import type { AnalyticsSummary } from "@/types";

export default function AdminPage() {
  const { user, loading, error } = useStaffGuard();
  const [stats, setStats] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    if (user) {
      api.get<AnalyticsSummary>("/api/analytics/summary").then(setStats);
    }
  }, [user]);

  if (loading) return <p className="text-brand-muted">Loading analytics…</p>;
  if (error) return <p className="text-brand-error">{error}</p>;
  if (!stats) return <p className="text-brand-muted">Loading analytics…</p>;

  const cards = [
    { label: "Total users", value: stats.total_users },
    { label: "Active users (7d)", value: stats.active_users_7d },
    { label: "Total bookings", value: stats.total_bookings },
    { label: "Revenue (WON)", value: stats.total_revenue_won.toLocaleString() },
    { label: "WON in circulation", value: stats.won_in_circulation.toLocaleString() },
    { label: "Scheduled flights", value: stats.flights_scheduled },
    { label: "Active flights", value: stats.flights_active },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Staff analytics</h1>
        <p className="text-brand-muted">Logged in as {user?.username} ({user?.role})</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((c) => (
          <div key={c.label} className="rounded-xl border border-white/10 bg-brand-surface p-5">
            <p className="text-sm text-brand-muted">{c.label}</p>
            <p className="mt-1 text-2xl font-bold">{c.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link
          href="/admin/flights"
          className="rounded-xl border border-brand-primary/40 bg-brand-surface p-6 hover:border-brand-primary"
        >
          <h2 className="text-lg font-semibold">Flight dispatcher</h2>
          <p className="mt-1 text-sm text-brand-muted">
            Schedule flights, assign aircraft, update live status
          </p>
        </Link>
        <Link
          href="/admin/users"
          className="rounded-xl border border-brand-accent/40 bg-brand-surface p-6 hover:border-brand-accent"
        >
          <h2 className="text-lg font-semibold">User management</h2>
          <p className="mt-1 text-sm text-brand-muted">
            WON adjustments, roles, transaction history
          </p>
        </Link>
        <Link
          href="/admin/staff"
          className="rounded-xl border border-emerald-500/40 bg-brand-surface p-6 hover:border-emerald-500"
        >
          <h2 className="text-lg font-semibold">Staff duty</h2>
          <p className="mt-1 text-sm text-brand-muted">
            Clock-in/out logs and total hours from Discord
          </p>
        </Link>
        <Link
          href="/admin/pireps"
          className="rounded-xl border border-amber-500/40 bg-brand-surface p-6 hover:border-amber-500"
        >
          <h2 className="text-lg font-semibold">PIREP review</h2>
          <p className="mt-1 text-sm text-brand-muted">
            Approve flights, pay WON, promote ranks
          </p>
        </Link>
      </div>
    </div>
  );
}
