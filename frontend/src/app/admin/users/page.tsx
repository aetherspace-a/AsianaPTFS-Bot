"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useStaffGuard } from "@/hooks/useStaffGuard";
import { brandingConfig } from "@/lib/branding";
import type { Transaction, User, UserRole } from "@/types";

export default function AdminUsersPage() {
  const { user: currentUser, loading, error: guardError } = useStaffGuard();
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<User | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [adjustAmount, setAdjustAmount] = useState("");
  const [newRole, setNewRole] = useState<UserRole>("User");
  const [message, setMessage] = useState("");

  const sym = brandingConfig.economy.currency_symbol;
  const isAdmin = currentUser?.role === "Admin";

  const loadUsers = useCallback(() => {
    const q = search ? `?search=${encodeURIComponent(search)}` : "";
    api.get<User[]>(`/api/admin/users${q}`).then(setUsers);
  }, [search]);

  useEffect(() => {
    if (!currentUser) return;
    const timer = setTimeout(loadUsers, 300);
    return () => clearTimeout(timer);
  }, [currentUser, loadUsers, search]);

  async function selectUser(u: User) {
    setSelected(u);
    setNewRole(u.role);
    setMessage("");
    const txs = await api.get<Transaction[]>(`/api/admin/users/${u.discord_id}/transactions`);
    setTransactions(txs);
  }

  async function adjustBalance() {
    if (!selected || !adjustAmount) return;
    try {
      const updated = await api.post<User>(`/api/users/${selected.discord_id}/balance`, {
        amount: parseInt(adjustAmount, 10),
        reason: "Staff adjustment",
      });
      setMessage(`Balance updated to ${sym}${updated.won_balance.toLocaleString()}`);
      setAdjustAmount("");
      loadUsers();
      selectUser(updated);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Adjustment failed");
    }
  }

  async function saveRole() {
    if (!selected || !isAdmin) return;
    try {
      const updated = await api.patch<User>(
        `/api/admin/users/${selected.discord_id}/role?role=${newRole}`,
        {},
      );
      setMessage(`Role set to ${updated.role}`);
      loadUsers();
      selectUser(updated);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Role update failed");
    }
  }

  if (loading) return <p className="text-brand-muted">Loading…</p>;
  if (guardError) return <p className="text-brand-error">{guardError}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">User management</h1>
        <p className="text-brand-muted">Adjust balances, roles, and view transaction history</p>
      </div>

      <input
        type="search"
        placeholder="Search username or Discord ID…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && loadUsers()}
        className="w-full max-w-md rounded-lg border border-white/20 bg-brand-surface px-4 py-2"
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <ul className="max-h-[480px] space-y-2 overflow-y-auto rounded-xl border border-white/10 bg-brand-surface p-3">
          {users.map((u) => (
            <li key={u.id}>
              <button
                type="button"
                onClick={() => selectUser(u)}
                className={`w-full rounded-lg px-3 py-2 text-left text-sm ${
                  selected?.id === u.id ? "bg-brand-primary/20" : "hover:bg-white/5"
                }`}
              >
                <span className="font-medium">{u.username}</span>
                <span className="ml-2 text-brand-muted">
                  {sym}
                  {u.won_balance.toLocaleString()} · {u.role}
                </span>
              </button>
            </li>
          ))}
        </ul>

        <div className="rounded-xl border border-white/10 bg-brand-surface p-5">
          {selected ? (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold">{selected.username}</h2>
                <p className="text-sm text-brand-muted">Discord: {selected.discord_id}</p>
                <p className="mt-2 text-2xl font-bold text-brand-accent">
                  {sym}
                  {selected.won_balance.toLocaleString()}
                </p>
              </div>

              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="WON delta (+/-)"
                  value={adjustAmount}
                  onChange={(e) => setAdjustAmount(e.target.value)}
                  className="flex-1 rounded-lg border border-white/20 bg-brand-background px-3 py-2"
                />
                <button
                  type="button"
                  onClick={adjustBalance}
                  className="rounded-lg bg-brand-primary px-4 py-2 text-sm text-white"
                >
                  Apply
                </button>
              </div>

              {isAdmin && (
                <div className="flex gap-2">
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value as UserRole)}
                    className="flex-1 rounded-lg border border-white/20 bg-brand-background px-3 py-2"
                  >
                    {(["User", "Staff", "Admin"] as UserRole[]).map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={saveRole}
                    className="rounded-lg border border-white/20 px-4 py-2 text-sm"
                  >
                    Set role
                  </button>
                </div>
              )}

              <div>
                <h3 className="mb-2 font-semibold">Transaction history</h3>
                <ul className="max-h-48 space-y-1 overflow-y-auto text-sm">
                  {transactions.length === 0 ? (
                    <li className="text-brand-muted">No transactions</li>
                  ) : (
                    transactions.map((t) => (
                      <li key={t.id} className="flex justify-between border-b border-white/5 py-1">
                        <span>
                          {t.type}{" "}
                          <span className={t.amount >= 0 ? "text-brand-success" : "text-brand-error"}>
                            {t.amount >= 0 ? "+" : ""}
                            {t.amount}
                          </span>
                        </span>
                        <span className="text-brand-muted">
                          {new Date(t.timestamp).toLocaleString()}
                        </span>
                      </li>
                    ))
                  )}
                </ul>
              </div>
            </div>
          ) : (
            <p className="text-brand-muted">Select a user to manage</p>
          )}
        </div>
      </div>

      {message && <p className="text-sm text-brand-accent">{message}</p>}
    </div>
  );
}
