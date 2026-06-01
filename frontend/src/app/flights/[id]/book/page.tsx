"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";
import { SeatMap } from "@/components/SeatMap";
import type { Flight, SeatClass, SeatMap as SeatMapType } from "@/types";

export default function BookFlightPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [flight, setFlight] = useState<Flight | null>(null);
  const [seatmap, setSeatmap] = useState<SeatMapType | null>(null);
  const [selection, setSelection] = useState<{ seat: string; seatClass: SeatClass } | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/");
      return;
    }
    Promise.all([
      api.get<Flight>(`/api/flights/${id}`, false),
      api.get<SeatMapType>(`/api/bookings/flight/${id}/seatmap`, false),
    ]).then(([f, s]) => {
      setFlight(f);
      setSeatmap(s);
    });
  }, [id, router]);

  async function checkout() {
    if (!selection) {
      setMessage("Select a seat first.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      await api.post("/api/bookings", {
        flight_id: id,
        seat_number: selection.seat,
        seat_class: selection.seatClass,
      });
      setMessage("Booking confirmed! WON deducted from your balance.");
      setTimeout(() => router.push("/dashboard"), 1500);
    } catch (e) {
      setMessage(e instanceof ApiError ? e.message : "Booking failed");
    } finally {
      setLoading(false);
    }
  }

  if (!flight || !seatmap) return <p className="text-brand-muted">Loading seat map…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Book {flight.flight_number}</h1>
        <p className="text-brand-muted">
          {flight.departure} → {flight.arrival}
        </p>
      </div>
      <SeatMap seatmap={seatmap} onSelect={(seat, seatClass) => setSelection({ seat, seatClass })} />
      <button
        type="button"
        disabled={loading || !selection}
        onClick={checkout}
        className="rounded-lg bg-brand-primary px-6 py-3 font-medium text-white disabled:opacity-50"
      >
        {loading ? "Processing…" : "Confirm booking"}
      </button>
      {message && <p className="text-sm text-brand-accent">{message}</p>}
    </div>
  );
}
