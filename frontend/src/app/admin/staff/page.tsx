"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useStaffGuard } from "@/hooks/useStaffGuard";
import type { StaffDutySummary, StaffShift } from "@/types";

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

export default function AdminStaffPage() {
  const { user, loading, error: guardError } = useStaffGuard();
  const [summary, setSummary] = useState<StaffDutySummary[]>([]);
  const [shifts, setShifts] = useState<StaffShift[]>([]);
  const [activeOnly, setActiveOnly] = useState(false);

  useEffect(() => {
    if (!user) return;
    api.get<StaffDutySummary[]>("/api/admin/staff/summary").then(setSummary);
  }, [user]);

  useEffect(() => {
    if (!user) return;
    api
      .get<StaffShift[]>(`/api/admin/staff/shifts?active_only=${activeOnly}`)
      .then(setShifts);
  }, [user, activeOnly]);

  if (loading) return <p className="text-brand-muted">Loading…</p>;
  if (guardError) return <p className="text-brand-error">{guardError}</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Staff duty tracking</h1>
        <p className="text-brand-muted">
          Shifts recorded via Discord <code className="text-brand-accent">/clockin</code> and{" "}
          <code className="text-brand-accent">/clockout</code>
        </p>
      </div>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Hours summary</h2>
        <div className="overflow-x-auto rounded-xl border border-white/10">
          <table className="w-full text-left text-sm">
            <thead className="bg-brand-surface text-brand-muted">
              <tr>
                <th className="px-4 py-3">Staff</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Shifts</th>
                <th className="px-4 py-3">Total hours</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {summary.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-brand-muted">
                    No duty shifts recorded yet.
                  </td>
                </tr>
              ) : (
                summary.map((s) => (
                  <tr key={s.user_id} className="border-t border-white/10">
                    <td className="px-4 py-3 font-medium">{s.username}</td>
                    <td className="px-4 py-3">{s.role}</td>
                    <td className="px-4 py-3">{s.total_shifts}</td>
                    <td className="px-4 py-3">{formatDuration(s.total_seconds)}</td>
                    <td className="px-4 py-3">
                      {s.is_clocked_in ? (
                        <span className="rounded-full bg-brand-success/20 px-2 py-0.5 text-brand-success">
                          On duty
                        </span>
                      ) : (
                        <span className="text-brand-muted">Off duty</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Shift log</h2>
          <label className="flex items-center gap-2 text-sm text-brand-muted">
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(e) => setActiveOnly(e.target.checked)}
            />
            Active shifts only
          </label>
        </div>
        <ul className="space-y-2">
          {shifts.map((shift) => (
            <li
              key={shift.id}
              className="rounded-lg border border-white/10 bg-brand-surface px-4 py-3 text-sm"
            >
              <span className="font-medium">{shift.user?.username ?? shift.user_id}</span>
              <span className="mx-2 text-brand-muted">·</span>
              {new Date(shift.clock_in).toLocaleString()}
              {shift.clock_out ? (
                <> → {new Date(shift.clock_out).toLocaleString()}</>
              ) : (
                <span className="ml-2 text-brand-success">(active)</span>
              )}
              {shift.duration_seconds != null && (
                <span className="ml-2 text-brand-accent">
                  ({formatDuration(shift.duration_seconds)})
                </span>
              )}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
