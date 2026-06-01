import Link from "next/link";
import type { Flight } from "@/types";

const statusColors: Record<string, string> = {
  Scheduled: "bg-blue-500/20 text-blue-300",
  Boarding: "bg-amber-500/20 text-amber-300",
  "In-Air": "bg-emerald-500/20 text-emerald-300",
  Landed: "bg-gray-500/20 text-gray-300",
};

export function FlightCard({ flight, bookable = true }: { flight: Flight; bookable?: boolean }) {
  const dep = new Date(flight.departure_time).toLocaleString();

  return (
    <article className="rounded-xl border border-white/10 bg-brand-surface p-5 shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-2xl font-bold">{flight.flight_number}</p>
          <p className="mt-1 text-brand-muted">
            {flight.departure} → {flight.arrival}
            {flight.aircraft ? ` · ${flight.aircraft}` : ""}
          </p>
          <p className="mt-2 text-sm">{dep}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusColors[flight.status] ?? ""}`}>
          {flight.status}
        </span>
      </div>
      {bookable && flight.status !== "Landed" && (
        <Link
          href={`/flights/${flight.id}/book`}
          className="mt-4 inline-block rounded-lg bg-brand-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          Select seats
        </Link>
      )}
    </article>
  );
}
