"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setToken } from "@/lib/auth";

function CallbackInner() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    const token = params.get("token");
    if (token) {
      setToken(token);
      router.replace("/dashboard");
    } else {
      router.replace("/");
    }
  }, [params, router]);

  return (
    <div className="flex min-h-[40vh] items-center justify-center">
      <p className="text-brand-muted">Signing you in…</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<p className="text-brand-muted">Loading…</p>}>
      <CallbackInner />
    </Suspense>
  );
}
