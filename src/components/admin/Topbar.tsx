"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bell, ChevronDown, LogOut, Menu, Search, Settings, UserCircle2 } from "lucide-react";
import { clearAdminAuth, getAdminEmail } from "@/lib/auth";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

const notifications = [
  { id: 1, text: "New booking from Rohan Verma for Sunset Bay Villa", time: "5m ago" },
  { id: 2, text: "Payment received for BK-24013", time: "1h ago" },
  { id: 3, text: "New 5-star review on Azure Cliffside Villa", time: "3h ago" },
];

export function Topbar({ onOpenMobileSidebar }: { onOpenMobileSidebar: () => void }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setEmail(getAdminEmail());
  }, []);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setNotifOpen(false);
        setProfileOpen(false);
      }
    }
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  function handleLogout() {
    clearAdminAuth();
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-slate-100 bg-white/90 px-4 py-3.5 backdrop-blur-md sm:px-6 dark:border-white/10 dark:bg-slate-900/90">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="rounded-lg p-2 text-primary-800 hover:bg-primary-50 lg:hidden dark:text-primary-200 dark:hover:bg-white/10"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="hidden items-center gap-2 rounded-full bg-slate-100 px-4 py-2 sm:flex dark:bg-white/5">
          <Search className="h-4 w-4 text-slate-400" />
          <input
            placeholder="Search bookings, guests, properties..."
            className="w-56 bg-transparent text-sm text-slate-600 outline-none placeholder:text-slate-400 lg:w-72 dark:text-slate-200"
          />
        </div>
      </div>

      <div ref={ref} className="flex items-center gap-3">
        <ThemeToggle />

        <div className="relative">
          <button
            onClick={() => {
              setNotifOpen((o) => !o);
              setProfileOpen(false);
            }}
            className="relative flex h-10 w-10 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-primary-50 hover:text-primary-700 dark:text-slate-400 dark:hover:bg-white/10 dark:hover:text-white"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute right-2 top-2 h-2 w-2 animate-pulse-ring rounded-full bg-accent-600" />
          </button>

          {notifOpen && (
            <div className="animate-scale-in absolute right-0 mt-2 w-80 origin-top-right rounded-2xl bg-white p-2 shadow-xl shadow-primary-900/15 ring-1 ring-slate-100 dark:bg-slate-800 dark:shadow-black/40 dark:ring-white/10">
              <p className="px-3 py-2 text-xs font-bold uppercase tracking-wide text-slate-400">
                Notifications
              </p>
              {notifications.map((n) => (
                <div
                  key={n.id}
                  className="rounded-xl px-3 py-2.5 text-sm transition-colors hover:bg-primary-50 dark:hover:bg-white/10"
                >
                  <p className="text-slate-700 dark:text-slate-200">{n.text}</p>
                  <p className="mt-0.5 text-xs text-slate-400">{n.time}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => {
              setProfileOpen((o) => !o);
              setNotifOpen(false);
            }}
            className="flex items-center gap-2 rounded-full py-1 pl-1 pr-2.5 transition-colors hover:bg-primary-50 dark:hover:bg-white/10"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-700 text-sm font-bold text-white">
              {email ? email[0].toUpperCase() : "A"}
            </span>
            <span className="hidden text-sm font-medium text-slate-600 sm:block dark:text-slate-300">
              {email || "Admin"}
            </span>
            <ChevronDown className="hidden h-4 w-4 text-slate-400 sm:block" />
          </button>

          {profileOpen && (
            <div className="animate-scale-in absolute right-0 mt-2 w-56 origin-top-right rounded-2xl bg-white p-2 shadow-xl shadow-primary-900/15 ring-1 ring-slate-100 dark:bg-slate-800 dark:shadow-black/40 dark:ring-white/10">
              <div className="px-3 py-2">
                <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">{email || "admin"}</p>
                <p className="text-xs text-slate-400">Zoiko Rooms Admin</p>
              </div>
              <Link
                href="/settings"
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-600 hover:bg-primary-50 dark:text-slate-300 dark:hover:bg-white/10"
              >
                <UserCircle2 className="h-4 w-4" /> Profile
              </Link>
              <Link
                href="/settings"
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-600 hover:bg-primary-50 dark:text-slate-300 dark:hover:bg-white/10"
              >
                <Settings className="h-4 w-4" /> Settings
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
