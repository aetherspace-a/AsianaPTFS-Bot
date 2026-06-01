"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";
import type { User } from "@/types";

export function useStaffGuard(adminOnly = false) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/");
      return;
    }
    api
      .get<User>("/api/users/me")
      .then((u) => {
        const isStaff = u.role === "Staff" || u.role === "Admin";
        const isAdmin = u.role === "Admin";
        if (!isStaff || (adminOnly && !isAdmin)) {
          setError(adminOnly ? "Admin access required." : "Staff access required.");
          return;
        }
        setUser(u);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [router, adminOnly]);

  return { user, loading, error };
}
