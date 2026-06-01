"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useStaffGuard } from "@/hooks/useStaffGuard";
import type { Flight, FlightStatus } from "@/types";

const STATUSES: FlightStatus[] = ["Scheduled", "Boarding", "In-Air", "Landed"];

const emptyForm = {
  flight_number: "",
  departure: "",
  arrival: "",
  aircraft: "",
  departure_time: "",
  status: "Scheduled" as FlightStatus,
};

export default function AdminFlightsPage() {
  const { user, loading, error: guardError } = useStaffGuard();
  const [flights, setFlights] = useState<Flight[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const loadFlights = useCallback(() => {
    api.get<Flight[]>("/api/flights").then(setFlights).catch(() => setFlights([]));
  }, []);

  useEffect(() => {
    if (user) loadFlights();
  }, [user, loadFlights]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await api.post("/api/flights", {
        ...form,
        aircraft: form.aircraft || null,
        departure_time: new Date(form.departure_time).toISOString(),
      });
      setForm(emptyForm);
      setMessage("Flight scheduled.");
      loadFlights();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to create flight");
    } finally {
      setBusy(false);
    }
  }

  async function updateStatus(flight: Flight, status: FlightStatus) {
    try {
      await api.patch(`/api/flights/${flight.id}`, { status });
      loadFlights();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Status update failed");
    }
  }

  async function deleteFlight(id: string) {
    if (!confirm("Delete this flight and all bookings?")) return;
    try {
      await api.delete(`/api/flights/${id}`);
      loadFlights();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  if (loading) return <p className="text-brand-muted">Loading…</p>;
  if (guardError) return <p className="text-brand-error">{guardError}</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Flight dispatcher</h1>
        <p className="text-brand-muted">Schedule flights and update live status</p>
      </div>

      <form
        onSubmit={handleCreate}
        className="grid gap-4 rounded-xl border border-white/10 bg-brand-surface p-6 md:grid-cols-2 lg:grid-cols-3"
      >
        <h2 className="md:col-span-2 lg:col-span-3 text-lg font-semibold">Schedule new flight</h2>
        {(
          [
            ["flight_number", "Flight number", "text"],
            ["departure", "Departure (ICAO)", "text"],
            ["arrival", "Arrival (ICAO)", "text"],
            ["aircraft", "Aircraft", "text"],
            ["departure_time", "Departure time", "datetime-local"],
          ] as const
        ).map(([key, label, type]) => (
          <label key={key} className="block text-sm">
            <span className="text-brand-muted">{label}</span>
            <input
              required={key !== "aircraft"}
              type={type}
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
            />
          </label>
        ))}
        <label className="block text-sm">
          <span className="text-brand-muted">Initial status</span>
          <select
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value as FlightStatus })}
            className="mt-1 w-full rounded-lg border border-white/20 bg-brand-background px-3 py-2"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="submit"
            disabled={busy}
            className="rounded-lg bg-brand-primary px-6 py-2 font-medium text-white disabled:opacity-50"
          >
            {busy ? "Saving…" : "Create flight"}
          </button>
        </div>
      </form>

      {message && <p className="text-sm text-brand-accent">{message}</p>}

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Active schedule ({flights.length})</h2>
        {flights.map((f) => (
          <div
            key={f.id}
            className="flex flex-col gap-4 rounded-xl border border-white/10 bg-brand-surface p-4 lg:flex-row lg:items-center lg:justify-between"
          >
            <div>
              <p className="text-xl font-bold">{f.flight_number}</p>
              <p className="text-brand-muted">
                {f.departure} → {f.arrival}
                {f.aircraft ? ` · ${f.aircraft}` : ""}
              </p>
              <p className="text-sm text-brand-muted">
                {new Date(f.departure_time).toLocaleString()} ·{" "}
                <span className="text-brand-accent">{f.status}</span>
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {STATUSES.map((s) => (
                <button
                  key={s}
                  type="button"
                  disabled={f.status === s}
                  onClick={() => updateStatus(f, s)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                    f.status === s
                      ? "bg-brand-accent text-brand-secondary"
                      : "bg-white/10 hover:bg-white/20"
                  }`}
                >
                  {s}
                </button>
              ))}
              <button
                type="button"
                onClick={() => deleteFlight(f.id)}
                className="rounded-lg border border-brand-error/50 px-3 py-1.5 text-xs text-brand-error hover:bg-brand-error/10"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
