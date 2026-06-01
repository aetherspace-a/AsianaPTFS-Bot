"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/admin", label: "Overview", exact: true },
  { href: "/admin/flights", label: "Flight dispatcher" },
  { href: "/admin/users", label: "User management" },
  { href: "/admin/staff", label: "Staff duty" },
  { href: "/admin/pireps", label: "PIREPs" },
];

export function AdminNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-wrap gap-2 border-b border-white/10 pb-4">
      {links.map((l) => {
        const active = l.exact ? pathname === l.href : pathname.startsWith(l.href);
        return (
          <Link
            key={l.href}
            href={l.href}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
              active
                ? "bg-brand-primary text-white"
                : "bg-white/5 text-brand-muted hover:bg-white/10 hover:text-brand-text"
            }`}
          >
            {l.label}
          </Link>
        );
      })}
    </nav>
  );
}
