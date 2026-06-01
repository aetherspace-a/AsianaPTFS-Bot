"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FlightCard } from "@/components/FlightCard";
import type { Flight } from "@/types";

export default function TrackerPage() {
  const [flights, setFlights] = useState<Flight[]>([]);

  useEffect(() => {
    const load = () => {
      api
        .get<Flight[]>("/api/flights?active_only=true", false)
        .then(setFlights)
        .catch(() => setFlights([]));
    };
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Live flight tracker</h1>
        <p className="text-brand-muted">Refreshes every 15 seconds</p>
      </div>
      {flights.length === 0 ? (
        <p className="rounded-xl border border-white/10 bg-brand-surface p-8 text-center text-brand-muted">
          No active flights right now.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {flights.map((f) => (
            <FlightCard key={f.id} flight={f} bookable={false} />
          ))}
        </div>
      )}
    </div>
  );
}
