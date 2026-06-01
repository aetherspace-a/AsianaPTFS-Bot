"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FlightCard } from "@/components/FlightCard";
import type { Flight } from "@/types";

export default function FlightsPage() {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Flight[]>("/api/flights", false)
      .then(setFlights)
      .finally(() => setLoading(false));
  }, []);

  const filtered = flights.filter(
    (f) =>
      f.flight_number.toLowerCase().includes(query.toLowerCase()) ||
      f.departure.toLowerCase().includes(query.toLowerCase()) ||
      f.arrival.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Flight search</h1>
        <p className="text-brand-muted">Find and book your next virtual flight</p>
      </div>
      <input
        type="search"
        placeholder="Search by flight number or airport…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full max-w-md rounded-lg border border-white/20 bg-brand-surface px-4 py-2 outline-none focus:border-brand-primary"
      />
      {loading ? (
        <p className="text-brand-muted">Loading flights…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {filtered.map((f) => (
            <FlightCard key={f.id} flight={f} />
          ))}
        </div>
      )}
      {!loading && filtered.length === 0 && (
        <p className="text-brand-muted">No flights match your search.</p>
      )}
    </div>
  );
}
