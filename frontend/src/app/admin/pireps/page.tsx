"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useStaffGuard } from "@/hooks/useStaffGuard";
import { brandingConfig } from "@/lib/branding";
import type { Pirep } from "@/types";

type Filter = "Pending" | "Approved" | "Rejected" | "All";

export default function AdminPirepsPage() {
  const { user, loading, error: guardError } = useStaffGuard();
  const [pireps, setPireps] = useState<Pirep[]>([]);
  const [filter, setFilter] = useState<Filter>("Pending");
  const [message, setMessage] = useState("");
  const sym = brandingConfig.economy.currency_symbol;

  const load = useCallback(() => {
    const q = filter === "All" ? "" : `?status=${filter}`;
    api.get<Pirep[]>(`/api/pireps/admin/list${q}`).then(setPireps);
  }, [filter]);

  useEffect(() => {
    if (user) load();
  }, [user, load]);

  async function approve(id: string) {
    try {
      await api.post(`/api/pireps/admin/${id}/approve`, {});
      setMessage("PIREP approved — hours, WON, and rank updated.");
      load();
    } catch (e) {
      setMessage(e instanceof ApiError ? e.message : "Approve failed");
    }
  }

  async function reject(id: string) {
    const reason = prompt("Rejection reason (optional):") ?? "";
    try {
      await api.post(`/api/pireps/admin/${id}/reject`, { reason: reason || null });
      setMessage("PIREP rejected.");
      load();
    } catch (e) {
      setMessage(e instanceof ApiError ? e.message : "Reject failed");
    }
  }

  if (loading) return <p className="text-brand-muted">Loading…</p>;
  if (guardError) return <p className="text-brand-error">{guardError}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">PIREP review</h1>
        <p className="text-brand-muted">Approve or reject pilot flight reports</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {(["Pending", "Approved", "Rejected", "All"] as Filter[]).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`rounded-lg px-4 py-2 text-sm ${
              filter === f ? "bg-brand-primary text-white" : "bg-white/10"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {message && <p className="text-sm text-brand-accent">{message}</p>}

      <ul className="space-y-4">
        {pireps.map((p) => (
          <li key={p.id} className="rounded-xl border border-white/10 bg-brand-surface p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="font-semibold">
                  {p.user?.username ?? "Pilot"} — {p.flight?.flight_number}
                </p>
                <p className="text-sm text-brand-muted">
                  {p.flight?.departure} → {p.flight?.arrival} ·{" "}
                  {Math.floor(p.flight_time_minutes / 60)}h {p.flight_time_minutes % 60}m ·{" "}
                  {p.landing_rate_fpm} fpm
                  {p.fuel_used_lbs != null ? ` · ${p.fuel_used_lbs} lbs fuel` : ""}
                </p>
                {p.notes && <p className="mt-2 text-sm italic text-brand-muted">{p.notes}</p>}
                <p className="mt-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      p.status === "Pending"
                        ? "bg-amber-500/20 text-amber-300"
                        : p.status === "Approved"
                          ? "bg-brand-success/20 text-brand-success"
                          : "bg-brand-error/20 text-brand-error"
                    }`}
                  >
                    {p.status}
                  </span>
                  {p.estimated_bonus != null && p.status === "Pending" && (
                    <span className="ml-2 text-sm text-brand-accent">
                      Est. {sym}
                      {p.estimated_bonus.toLocaleString()}
                    </span>
                  )}
                  {p.won_bonus != null && p.status === "Approved" && (
                    <span className="ml-2 text-sm text-brand-success">
                      Paid {sym}
                      {p.won_bonus.toLocaleString()}
                    </span>
                  )}
                </p>
              </div>
              {p.status === "Pending" && (
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => approve(p.id)}
                    className="rounded-lg bg-brand-success px-4 py-2 text-sm font-medium text-white"
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    onClick={() => reject(p.id)}
                    className="rounded-lg border border-brand-error px-4 py-2 text-sm text-brand-error"
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
      {pireps.length === 0 && <p className="text-brand-muted">No PIREPs in this category.</p>}
    </div>
  );
}
