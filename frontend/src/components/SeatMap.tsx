"use client";

import { useMemo, useState } from "react";
import type { SeatClass, SeatMap as SeatMapType } from "@/types";

const CLASS_PRICES: Record<SeatClass, number> = {
  Economy: 1000,
  Business: 2500,
  First: 5000,
};

interface Props {
  seatmap: SeatMapType;
  onSelect: (seat: string, seatClass: SeatClass) => void;
}

export function SeatMap({ seatmap, onSelect }: Props) {
  const [seatClass, setSeatClass] = useState<SeatClass>("Economy");
  const [selected, setSelected] = useState<string | null>(null);

  const grid = useMemo(() => {
    const rows: Record<number, typeof seatmap.seats> = {};
    for (const seat of seatmap.seats) {
      const row = parseInt(seat.seat_number, 10);
      if (!rows[row]) rows[row] = [];
      rows[row].push(seat);
    }
    return Object.entries(rows)
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([row, seats]) => ({
        row: Number(row),
        seats: seats.sort((a, b) => a.seat_number.localeCompare(b.seat_number)),
      }));
  }, [seatmap.seats]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {(["Economy", "Business", "First"] as SeatClass[]).map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setSeatClass(c)}
            className={`rounded-lg px-4 py-2 text-sm ${
              seatClass === c
                ? "bg-brand-accent text-brand-secondary font-semibold"
                : "bg-white/5 text-brand-muted"
            }`}
          >
            {c} — {CLASS_PRICES[c].toLocaleString()} WON
          </button>
        ))}
      </div>

      <div className="overflow-x-auto rounded-xl border border-white/10 bg-brand-surface p-4">
        <div className="mx-auto mb-4 h-8 w-48 rounded-t-full bg-white/10 text-center text-xs leading-8 text-brand-muted">
          COCKPIT
        </div>
        {grid.map(({ row, seats }) => (
          <div key={row} className="mb-2 flex items-center gap-2">
            <span className="w-6 text-xs text-brand-muted">{row}</span>
            <div className="flex flex-wrap gap-1">
              {seats.map((seat) => {
                const isSelected = selected === seat.seat_number;
                const disabled = !seat.available;
                return (
                  <button
                    key={seat.seat_number}
                    type="button"
                    disabled={disabled}
                    title={disabled ? "Taken" : seat.seat_number}
                    onClick={() => {
                      setSelected(seat.seat_number);
                      onSelect(seat.seat_number, seatClass);
                    }}
                    className={`h-8 w-8 rounded text-[10px] font-medium transition ${
                      disabled
                        ? "cursor-not-allowed bg-brand-error/30 text-brand-error"
                        : isSelected
                          ? "bg-brand-accent text-brand-secondary ring-2 ring-white"
                          : "bg-emerald-600/40 hover:bg-emerald-500/60"
                    }`}
                  >
                    {seat.seat_number.replace(String(row), "")}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      {selected && (
        <p className="text-sm text-brand-muted">
          Selected: <strong className="text-brand-text">{selected}</strong> ({seatClass})
        </p>
      )}
    </div>
  );
}
