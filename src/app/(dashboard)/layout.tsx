"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { AdminGuard } from "@/components/admin/AdminGuard";
import { ChatLauncherFab } from "@/components/admin/ChatLauncherFab";
import { AdminChatPanel } from "@/components/admin/chat/AdminChatPanel";
import { Sidebar } from "@/components/admin/Sidebar";
import { Topbar } from "@/components/admin/Topbar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const pathname = usePathname();

  return (
    <AdminGuard>
      <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
        <Sidebar
          collapsed={collapsed}
          onToggleCollapse={() => setCollapsed((c) => !c)}
          mobileOpen={mobileOpen}
          onCloseMobile={() => setMobileOpen(false)}
        />

        <div className="flex min-h-screen flex-1 flex-col lg:min-w-0">
          <Topbar onOpenMobileSidebar={() => setMobileOpen(true)} onToggleChat={() => setChatOpen((o) => !o)} />
          <main key={pathname} className="animate-fade-up flex-1 p-4 sm:p-6 lg:p-8">
            {children}
          </main>
        </div>
      </div>

      <AdminChatPanel open={chatOpen} onClose={() => setChatOpen(false)} />
      <ChatLauncherFab open={chatOpen} onToggle={() => setChatOpen((o) => !o)} />
    </AdminGuard>
  );
}
