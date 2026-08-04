"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Image as ImageIcon, Lock, User, Bell } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Switch } from "@/components/ui/Switch";
import { Logo } from "@/components/ui/Logo";
import { getAdminEmail } from "@/lib/auth";
import { getLogoUrl, setLogoUrl } from "@/lib/branding";
import { cn } from "@/lib/utils";

const tabs = [
  { key: "profile", label: "Profile", icon: User },
  { key: "branding", label: "Branding", icon: ImageIcon },
  { key: "notifications", label: "Notifications", icon: Bell },
  { key: "security", label: "Security", icon: Lock },
] as const;

export function SettingsTabs() {
  const [active, setActive] = useState<(typeof tabs)[number]["key"]>("branding");
  const [email, setEmail] = useState("");
  const [logoInput, setLogoInput] = useState("");
  const [toast, setToast] = useState("");
  const [notifs, setNotifs] = useState({ newBooking: true, payments: true, reviews: false, marketing: false });

  useEffect(() => {
    setEmail(getAdminEmail());
    setLogoInput(getLogoUrl());
  }, []);

  function showToast(message: string) {
    setToast(message);
    setTimeout(() => setToast(""), 2200);
  }

  function handleSaveLogo(e: React.FormEvent) {
    e.preventDefault();
    setLogoUrl(logoInput.trim());
    showToast("Logo updated across the site");
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[220px_1fr]">
      <div className="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActive(key)}
            className={cn(
              "flex items-center gap-2.5 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-semibold transition-all duration-200",
              active === key
                ? "bg-primary-700 text-white shadow-md shadow-primary-900/25"
                : "bg-white text-slate-600 ring-1 ring-slate-100 hover:bg-primary-50 hover:text-primary-700 dark:bg-slate-900 dark:text-slate-300 dark:ring-white/10 dark:hover:bg-primary-500/10 dark:hover:text-primary-300"
            )}
          >
            <Icon className="h-4 w-4" /> {label}
          </button>
        ))}
      </div>

      <div className="animate-fade-in rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-white/10">
        {active === "profile" && (
          <div className="max-w-md space-y-4">
            <h2 className="font-heading text-lg font-bold text-primary-900 dark:text-white">Profile Details</h2>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Full Name
              </label>
              <input
                defaultValue="Zoiko Admin"
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Email
              </label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Phone
              </label>
              <input
                placeholder="+91 98200 11223"
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
              />
            </div>
            <Button onClick={() => showToast("Profile updated")}>Save Changes</Button>
          </div>
        )}

        {active === "branding" && (
          <div className="max-w-md space-y-4">
            <h2 className="font-heading text-lg font-bold text-primary-900 dark:text-white">Brand Logo</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Paste a hosted image URL for your logo — it updates instantly across the website and admin
              panel.
            </p>

            <div className="flex items-center gap-4 rounded-xl bg-slate-50 p-4 ring-1 ring-slate-100 dark:bg-slate-800 dark:ring-white/10">
              <Logo src={logoInput || undefined} />
            </div>

            <form onSubmit={handleSaveLogo} className="space-y-3">
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  Logo Image URL
                </label>
                <input
                  value={logoInput}
                  onChange={(e) => setLogoInput(e.target.value)}
                  placeholder="https://your-cdn.com/zoiko-logo.png"
                  className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit">Save Logo</Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setLogoInput("");
                    setLogoUrl("");
                    showToast("Reverted to default logo");
                  }}
                >
                  Reset to Default
                </Button>
              </div>
            </form>
          </div>
        )}

        {active === "notifications" && (
          <div className="max-w-md space-y-4">
            <h2 className="font-heading text-lg font-bold text-primary-900 dark:text-white">Notification Preferences</h2>
            {[
              { key: "newBooking", label: "New booking alerts" },
              { key: "payments", label: "Payment confirmations" },
              { key: "reviews", label: "New review alerts" },
              { key: "marketing", label: "Marketing updates" },
            ].map((item) => (
              <div key={item.key} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800">
                <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{item.label}</span>
                <Switch
                  checked={notifs[item.key as keyof typeof notifs]}
                  onChange={(v) => setNotifs((n) => ({ ...n, [item.key]: v }))}
                />
              </div>
            ))}
            <Button onClick={() => showToast("Notification preferences saved")}>Save Preferences</Button>
          </div>
        )}

        {active === "security" && (
          <div className="max-w-md space-y-4">
            <h2 className="font-heading text-lg font-bold text-primary-900 dark:text-white">Change Password</h2>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Current Password
              </label>
              <input
                type="password"
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                New Password
              </label>
              <input
                type="password"
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
              />
            </div>
            <Button onClick={() => showToast("Password updated")}>Update Password</Button>
          </div>
        )}
      </div>

      {toast && (
        <div className="animate-fade-up fixed bottom-6 right-6 z-[300] flex items-center gap-2 rounded-xl bg-primary-900 px-4 py-3 text-sm font-medium text-white shadow-2xl">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" /> {toast}
        </div>
      )}
    </div>
  );
}
