"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, CalendarClock, CheckCircle2, DoorOpen, RefreshCw } from "lucide-react";
import { Obligation, Occupancy } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClientFetch } from "@/lib/api-client";
import { occupancyStatusTone } from "@/lib/status";
import { formatDate } from "@/lib/utils";

export function OccupancyManager() {
  const [occupancies, setOccupancies] = useState<Occupancy[]>([]);
  const [rentDue, setRentDue] = useState<Occupancy[]>([]);
  const [toast, setToast] = useState("");

  function showToast(message: string) {
    setToast(message);
    setTimeout(() => setToast(""), 3200);
  }

  const loadAll = useCallback(async () => {
    try {
      const [occ, due] = await Promise.all([
        apiClientFetch<Occupancy[]>("/api/occupancy"),
        apiClientFetch<Occupancy[]>("/api/occupancy/rent-due-check"),
      ]);
      setOccupancies(occ);
      setRentDue(due);
    } catch {
      showToast("Failed to load occupancies");
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  async function generateRent(id: number) {
    try {
      const obligation = await apiClientFetch<Obligation | null>(`/api/occupancy/${id}/generate-rent`, { method: "POST" });
      showToast(obligation ? `Rent obligation generated for ${formatDate(obligation.dueDate)}` : "No new rent obligation needed yet");
      loadAll();
    } catch {
      showToast("Failed to generate rent obligation");
    }
  }

  async function endOccupancy(id: number) {
    try {
      await apiClientFetch(`/api/occupancy/${id}/end`, { method: "POST" });
      showToast("Occupancy ended");
      loadAll();
    } catch {
      showToast("Failed to end occupancy");
    }
  }

  return (
    <div className="space-y-4">
      {rentDue.length > 0 && (
        <div className="flex items-start gap-3 rounded-2xl bg-amber-50 p-4 ring-1 ring-amber-200 dark:bg-amber-500/10 dark:ring-amber-500/20">
          <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600" />
          <div>
            <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">
              {rentDue.length} occupanc{rentDue.length === 1 ? "y has" : "ies have"} no upcoming rent obligation scheduled
            </p>
            <p className="mt-0.5 text-xs text-amber-700 dark:text-amber-400">
              No billing scheduler runs automatically — generate the next rent obligation manually below.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {occupancies.map((occupancy) => (
          <div
            key={occupancy.id}
            className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-white/10"
          >
            <div className="flex items-center justify-between">
              <p className="font-heading text-sm font-bold text-primary-900 dark:text-white">{occupancy.guestName}</p>
              <Badge tone={occupancyStatusTone[occupancy.status]}>{occupancy.status}</Badge>
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{occupancy.listingId}</p>
            <div className="mt-2 space-y-1 text-xs text-slate-500 dark:text-slate-400">
              <p className="flex items-center gap-1.5">
                <CalendarClock className="h-3.5 w-3.5" /> Moved in {occupancy.moveInDate ? formatDate(occupancy.moveInDate) : "—"}
              </p>
              <p className="flex items-center gap-1.5">
                <CalendarClock className="h-3.5 w-3.5" /> Lease ends {occupancy.expectedEndDate ? formatDate(occupancy.expectedEndDate) : "—"}
              </p>
            </div>
            {occupancy.status === "ACTIVE" && (
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="outline" className="flex-1" onClick={() => generateRent(occupancy.id)}>
                  <RefreshCw className="h-3.5 w-3.5" /> Generate Rent
                </Button>
                <Button size="sm" variant="outline" className="flex-1" onClick={() => endOccupancy(occupancy.id)}>
                  <DoorOpen className="h-3.5 w-3.5" /> End
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>

      {occupancies.length === 0 && (
        <p className="py-10 text-center text-sm text-slate-400 dark:text-slate-400">
          No active occupancies yet — confirm move-in from a signed agreement on the Leasing page.
        </p>
      )}

      {toast && (
        <div className="animate-fade-up fixed bottom-6 right-6 z-[300] flex max-w-sm items-center gap-2 rounded-xl bg-primary-900 px-4 py-3 text-sm font-medium text-white shadow-2xl">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" /> {toast}
        </div>
      )}
    </div>
  );
}
