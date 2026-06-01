"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, downloadFile } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";
import { brandingConfig } from "@/lib/branding";
import type { Booking, User } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/");
      return;
    }
    Promise.all([
      api.get<User>("/api/users/me"),
      api.get<Booking[]>("/api/bookings/me"),
    ])
      .then(([u, b]) => {
        setUser(u);
        setBookings(b);
      })
      .catch((e) => setError(e.message));
  }, [router]);

  if (error) return <p className="text-brand-error">{error}</p>;
  if (!user) return <p className="text-brand-muted">Loading dashboard…</p>;

  const upcoming = bookings.filter(
    (b) => b.flight && b.flight.status !== "Landed",
  );
  const past = bookings.filter((b) => b.flight?.status === "Landed");

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Welcome, {user.username}</h1>
        <p className="text-brand-muted">Your {brandingConfig.airline_name} pilot dashboard</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-brand-accent/30 bg-brand-surface p-6">
          <p className="text-sm text-brand-muted">{brandingConfig.economy.currency_name} balance</p>
          <p className="text-4xl font-bold text-brand-accent">
            {brandingConfig.economy.currency_symbol}
            {user.won_balance.toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl border border-white/10 bg-brand-surface p-6">
          <p className="text-sm text-brand-muted">Pilot rank</p>
          <p className="text-2xl font-bold">{user.pilot_rank ?? "Trainee"}</p>
          <p className="mt-1 text-brand-muted">
            {(user.total_flight_hours ?? 0).toFixed(1)} approved flight hours
          </p>
          <a
            href="/dashboard/log-flight"
            className="mt-4 inline-block rounded-lg bg-brand-primary px-4 py-2 text-sm font-medium text-white"
          >
            Log a flight (PIREP)
          </a>
        </div>
      </div>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Upcoming flights</h2>
        {upcoming.length === 0 ? (
          <p className="text-brand-muted">No upcoming bookings.</p>
        ) : (
          <ul className="space-y-3">
            {upcoming.map((b) => (
              <li
                key={b.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-white/10 bg-brand-surface p-4"
              >
                <div>
                  <span className="font-semibold">{b.flight?.flight_number}</span>
                  <span className="mx-2 text-brand-muted">·</span>
                  Seat {b.seat_number} ({b.seat_class})
                  <span className="mx-2 text-brand-muted">·</span>
                  {b.flight?.departure} → {b.flight?.arrival}
                </div>
                {(b.has_boarding_pass ?? true) && (
                  <button
                    type="button"
                    onClick={() =>
                      downloadFile(
                        `/api/bookings/${b.id}/boarding-pass`,
                        `boarding-pass-${b.flight?.flight_number ?? b.id}.png`,
                      )
                    }
                    className="rounded-lg bg-brand-accent px-3 py-1.5 text-sm font-medium text-brand-secondary hover:opacity-90"
                  >
                    Download boarding pass
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Flight history</h2>
        {past.length === 0 ? (
          <p className="text-brand-muted">No completed flights yet.</p>
        ) : (
          <ul className="space-y-3">
            {past.map((b) => (
              <li key={b.id} className="rounded-lg border border-white/10 bg-brand-surface/50 p-4 opacity-80">
                {b.flight?.flight_number} — Seat {b.seat_number}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
