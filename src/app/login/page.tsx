"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  BarChart3,
  BedDouble,
  CalendarCheck2,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { Button } from "@/components/ui/Button";
import { setAdminAuth } from "@/lib/auth";

const perks = [
  { icon: CalendarCheck2, text: "Manage bookings across hotels, villas & houses" },
  { icon: BarChart3, text: "Real-time revenue and occupancy analytics" },
  { icon: BedDouble, text: "Full control over rooms, rates and availability" },
];

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }
    setError("");
    setSubmitting(true);
    setTimeout(() => {
      setAdminAuth(email.trim());
      router.push("/");
    }, 900);
  }

  return (
    <main className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      <section className="relative hidden overflow-hidden bg-primary-900 lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="bg-noise pointer-events-none absolute inset-0 opacity-30" />
        <div
          className="absolute -left-24 top-10 h-72 w-72 animate-float rounded-full bg-accent-600/25 blur-3xl"
          aria-hidden
        />
        <div
          className="absolute -right-20 bottom-10 h-80 w-80 animate-float rounded-full bg-primary-400/20 blur-3xl"
          style={{ animationDelay: "1.2s" }}
          aria-hidden
        />

        <div className="relative animate-fade-up">
          <Logo variant="light" />
        </div>

        <div className="relative animate-fade-up stagger-2 max-w-md">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3.5 py-1.5 text-xs font-semibold text-primary-100 ring-1 ring-white/20">
            <Sparkles className="h-3.5 w-3.5 text-accent-400" /> Admin Control Center
          </span>
          <h1 className="mt-5 font-heading text-3xl font-extrabold leading-tight text-white">
            Run your entire property business from one dashboard
          </h1>
          <div className="mt-8 space-y-4">
            {perks.map((perk, i) => {
              const Icon = perk.icon;
              return (
                <div
                  key={perk.text}
                  className="animate-fade-up flex items-center gap-3 rounded-xl bg-white/5 p-3.5 ring-1 ring-white/10 transition-colors hover:bg-white/10"
                  style={{ animationDelay: `${0.3 + i * 0.1}s` }}
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent-600/90 text-white">
                    <Icon className="h-4.5 w-4.5" />
                  </span>
                  <p className="text-sm text-primary-100">{perk.text}</p>
                </div>
              );
            })}
          </div>
        </div>

        <p className="relative animate-fade-up stagger-4 text-xs text-primary-300">
          © {new Date().getFullYear()} Zoiko Rooms. All rights reserved.
        </p>
      </section>

      <section className="flex items-center justify-center bg-slate-50 px-4 py-12 sm:px-8">
        <div className="w-full max-w-md">
          <div className="mb-8 flex justify-center lg:hidden">
            <Logo />
          </div>

          <div className="animate-scale-in rounded-3xl bg-white p-8 shadow-xl shadow-primary-900/10 ring-1 ring-slate-100 sm:p-10">
            <h2 className="font-heading text-2xl font-extrabold text-primary-900">Welcome back</h2>
            <p className="mt-1.5 text-sm text-slate-500">Sign in to access the Zoiko Rooms admin panel.</p>

            <form onSubmit={handleSubmit} className="mt-7 space-y-4">
              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Email address
                </span>
                <div className="flex items-center gap-2 rounded-xl bg-slate-50 px-4 py-3 ring-1 ring-slate-200 transition-all focus-within:ring-2 focus-within:ring-primary-400">
                  <Mail className="h-4 w-4 shrink-0 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@zoikorooms.com"
                    autoComplete="username"
                    className="w-full bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400"
                  />
                </div>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Password
                </span>
                <div className="flex items-center gap-2 rounded-xl bg-slate-50 px-4 py-3 ring-1 ring-slate-200 transition-all focus-within:ring-2 focus-within:ring-primary-400">
                  <Lock className="h-4 w-4 shrink-0 text-slate-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    autoComplete="current-password"
                    className="w-full bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="shrink-0 text-slate-400 transition-colors hover:text-primary-600"
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </label>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-slate-500">
                  <input
                    type="checkbox"
                    checked={remember}
                    onChange={(e) => setRemember(e.target.checked)}
                    className="h-4 w-4 rounded accent-primary-700"
                  />
                  Remember me
                </label>
                <a href="#" className="font-medium text-primary-700 hover:text-accent-600">
                  Forgot password?
                </a>
              </div>

              {error && (
                <p className="animate-fade-in rounded-lg bg-accent-50 px-3 py-2 text-xs font-medium text-accent-700 ring-1 ring-accent-200">
                  {error}
                </p>
              )}

              <Button type="submit" variant="primary" size="lg" fullWidth loading={submitting}>
                {submitting ? "Signing you in" : "Sign in to Dashboard"}
              </Button>
            </form>

            <div className="mt-6 flex items-center gap-2 rounded-xl bg-primary-50 px-4 py-3 text-xs text-primary-700 ring-1 ring-primary-100">
              <ShieldCheck className="h-4 w-4 shrink-0" />
              Demo mode: enter any email &amp; password to explore the admin dashboard.
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
