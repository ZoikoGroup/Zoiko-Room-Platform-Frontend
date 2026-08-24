"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { UserGuard } from "@/components/user/UserGuard";
import { UserSidebar } from "@/components/user/UserSidebar";
import { UserTopbar } from "@/components/user/UserTopbar";

/**
 * Shell for the signed-in USER area. `/account/login` and `/account/register` sit
 * outside this route group so they render without the guard or the chrome.
 */
export default function AccountLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  return (
    <UserGuard>
      <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
        <UserSidebar
          collapsed={collapsed}
          onToggleCollapse={() => setCollapsed((c) => !c)}
          mobileOpen={mobileOpen}
          onCloseMobile={() => setMobileOpen(false)}
        />

        <div className="flex min-h-screen flex-1 flex-col lg:min-w-0">
          <UserTopbar onOpenMobileSidebar={() => setMobileOpen(true)} />
          <main key={pathname} className="animate-fade-up flex-1 p-4 sm:p-6 lg:p-8">
            {children}
          </main>
        </div>
      </div>
    </UserGuard>
  );
}
