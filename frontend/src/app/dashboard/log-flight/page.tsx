"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";
import type { EligibleFlight, Pirep } from "@/types";

export default function LogFlightPage() {
  const router = useRouter();
  const [flights, setFlights] = useState<EligibleFlight[]>([]);
  const [flightId, setFlightId] = useState("");
  const [hours, setHours] = useState(1);
  const [minutes, setMinutes] = useState(0);
  const [landingRate, setLandingRate] = useState(250);
  const [fuel, setFuel] = useState("");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/");
      return;
    }
    api.get<EligibleFlight[]>("/api/pireps/eligible-flights").then(setFlights);
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!flightId) {
      setMessage("Select a booked flight.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const pirep = await api.post<Pirep>("/api/pireps", {
        flight_id: flightId,
        flight_time_hours: hours,
        flight_time_minutes: minutes,
        landing_rate_fpm: landingRate,
        fuel_used_lbs: fuel ? parseInt(fuel, 10) : null,
        notes: notes || null,
      });
      setMessage(
        `PIREP submitted (Pending review). Est. bonus: ${pirep.estimated_bonus?.toLocaleString() ?? "—"} WON`,
      );
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Submission failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <Link href="/dashboard" className="text-sm text-brand-muted hover:text-brand-text">
          ← Dashboard
        </Link>
        <h1 className="mt-2 text-3xl font-bold">Log flight (PIREP)</h1>
        <p className="text-brand-muted">Submit your completed flight for staff approval</p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-white/10 bg-brand-surface p-6">
        <label className="block text-sm">
          <span className="text-brand-muted">Booked flight</span>
          <select
            required
            value={flightId}
            onChange={(e) => setFlightId(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
          >
            <option value="">Select flight…</option>
            {flights.map((f) => (
              <option key={f.flight_id} value={f.flight_id}>
                {f.flight_number} {f.departure}→{f.arrival} (Seat {f.seat_number})
              </option>
            ))}
          </select>
        </label>

        <div className="grid grid-cols-2 gap-4">
          <label className="block text-sm">
            <span className="text-brand-muted">Flight time (hours)</span>
            <input
              type="number"
              min={0}
              max={24}
              value={hours}
              onChange={(e) => setHours(parseInt(e.target.value, 10) || 0)}
              className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="text-brand-muted">Minutes</span>
            <input
              type="number"
              min={0}
              max={59}
              value={minutes}
              onChange={(e) => setMinutes(parseInt(e.target.value, 10) || 0)}
              className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
            />
          </label>
        </div>

        <label className="block text-sm">
          <span className="text-brand-muted">Landing rate (fpm)</span>
          <input
            type="number"
            min={0}
            required
            value={landingRate}
            onChange={(e) => setLandingRate(parseInt(e.target.value, 10) || 0)}
            className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
          />
          <span className="mt-1 block text-xs text-brand-muted">
            Softer landings (lower fpm) earn a higher WON multiplier
          </span>
        </label>

        <label className="block text-sm">
          <span className="text-brand-muted">Fuel used (lbs, optional)</span>
          <input
            type="number"
            min={0}
            value={fuel}
            onChange={(e) => setFuel(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
          />
        </label>

        <label className="block text-sm">
          <span className="text-brand-muted">Notes (optional)</span>
          <textarea
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
          />
        </label>

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-lg bg-brand-primary py-3 font-medium text-white disabled:opacity-50"
        >
          {busy ? "Submitting…" : "Submit PIREP"}
        </button>
      </form>

      {message && <p className="text-sm text-brand-accent">{message}</p>}
      {flights.length === 0 && (
        <p className="text-sm text-brand-warning">
          Book a flight first before logging a PIREP.
        </p>
      )}
    </div>
  );
}
