"use client";

import { MessageSquare } from "lucide-react";

interface ChatLauncherFabProps {
  open: boolean;
  onToggle: () => void;
}

/** Floating action button that opens/closes the same AdminChatPanel as the
 *  Topbar button. Hidden while the panel is open so it never floats on top of
 *  the full-screen (mobile) or docked (desktop) chat surface. */
export function ChatLauncherFab({ open, onToggle }: ChatLauncherFabProps) {
  if (open) return null;

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label="Open Zoiko assistant chat"
      title="Zoiko Assistant"
      className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-accent-600 text-white shadow-xl shadow-primary-900/30 transition-transform duration-200 hover:scale-105 hover:bg-accent-700 active:scale-95"
    >
      <MessageSquare className="h-6 w-6" />
      <span className="absolute right-1 top-1 h-3 w-3 rounded-full border-2 border-white bg-emerald-400" />
    </button>
  );
}
