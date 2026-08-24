"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronDown, LogOut, Menu, ShieldCheck, UserCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { userLogout } from "@/lib/user-auth";
import { useUserSession } from "@/components/user/UserSessionContext";
import { identityStatusLabel, identityStatusTone } from "@/lib/status";

export function UserTopbar({ onOpenMobileSidebar }: { onOpenMobileSidebar: () => void }) {
  const router = useRouter();
  const { user, identityStatus } = useUserSession();
  const [profileOpen, setProfileOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setProfileOpen(false);
    }
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  async function handleLogout() {
    await userLogout();
    router.push("/account/login");
    router.refresh();
  }

  const displayName = user?.fullName || user?.email || "My account";

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-slate-100 bg-white/90 px-4 py-3.5 backdrop-blur-md sm:px-6 dark:border-white/10 dark:bg-slate-900/90">
      <div className="flex min-w-0 items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="rounded-lg p-2 text-primary-800 hover:bg-primary-50 lg:hidden dark:text-primary-200 dark:hover:bg-white/10"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="min-w-0">
          <p className="truncate font-heading text-sm font-bold text-primary-900 dark:text-white">
            Hi, {user?.fullName?.split(" ")[0] || "there"}
          </p>
          <p className="truncate text-xs text-slate-400">Renter &amp; host workspace</p>
        </div>
      </div>

      <div ref={ref} className="flex items-center gap-3">
        <Link href="/account/identity" className="hidden sm:block">
          <Badge tone={identityStatusTone[identityStatus]} dot>
            <ShieldCheck className="h-3.5 w-3.5" /> {identityStatusLabel[identityStatus]}
          </Badge>
        </Link>

        <ThemeToggle />

        <div className="relative">
          <button
            onClick={() => setProfileOpen((o) => !o)}
            className="flex items-center gap-2 rounded-full py-1 pl-1 pr-2.5 transition-colors hover:bg-primary-50 dark:hover:bg-white/10"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-700 text-sm font-bold text-white">
              {displayName[0]?.toUpperCase() ?? "U"}
            </span>
            <span className="hidden max-w-[10rem] truncate text-sm font-medium text-slate-600 sm:block dark:text-slate-300">
              {displayName}
            </span>
            <ChevronDown className="hidden h-4 w-4 text-slate-400 sm:block" />
          </button>

          {profileOpen && (
            <div className="animate-scale-in absolute right-0 mt-2 w-60 origin-top-right rounded-2xl bg-white p-2 shadow-xl shadow-primary-900/15 ring-1 ring-slate-100 dark:bg-slate-800 dark:shadow-black/40 dark:ring-white/10">
              <div className="px-3 py-2">
                <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">{displayName}</p>
                <p className="truncate text-xs text-slate-400">{user?.email}</p>
              </div>
              <Link
                href="/account/profile"
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-600 hover:bg-primary-50 dark:text-slate-300 dark:hover:bg-white/10"
              >
                <UserCircle2 className="h-4 w-4" /> Profile
              </Link>
              <Link
                href="/account/identity"
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-600 hover:bg-primary-50 dark:text-slate-300 dark:hover:bg-white/10"
              >
                <ShieldCheck className="h-4 w-4" /> Identity Verification
              </Link>
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-accent-600 hover:bg-accent-50 dark:hover:bg-accent-500/10"
              >
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
