"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { CalendarClock, ClipboardList, Search } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { UserApplication } from "@/lib/types";
import { applicationStatusTone } from "@/lib/status";
import { formatDate } from "@/lib/utils";
import { errorMessage, listRentalApplications, withdrawRentalApplication } from "@/lib/user-api";
import { Card, EmptyState, Toast, useToast } from "@/components/user/ui";

export function ApplicationsManager() {
  const { toast, showToast } = useToast();
  const [applications, setApplications] = useState<UserApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [withdrawingId, setWithdrawingId] = useState<number | null>(null);

  const load = useCallback(async () => {
    try {
      setApplications(await listRentalApplications());
    } catch (err) {
      showToast(errorMessage(err, "Could not load your applications."), "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleWithdraw(id: number) {
    setWithdrawingId(id);
    try {
      const updated = await withdrawRentalApplication(id);
      setApplications((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
      showToast("Application withdrawn.");
    } catch (err) {
      showToast(errorMessage(err, "Could not withdraw this application."), "error");
    } finally {
      setWithdrawingId(null);
    }
  }

  if (loading) return <Loader label="Loading your applications" />;

  if (applications.length === 0) {
    return (
      <Card>
        <div className="flex flex-col items-center gap-4 py-10 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-300">
            <ClipboardList className="h-6 w-6" />
          </span>
          <EmptyState message="You have not applied for any rooms yet." />
          <Link href="/account/rent">
            <Button size="sm">
              <Search className="h-4 w-4" /> Browse available rooms
            </Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {applications.map((application) => (
        <Card key={application.id} className="flex flex-wrap items-center justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-heading text-sm font-bold text-primary-900 dark:text-white">
                {application.listingId}
              </p>
              <Badge tone={applicationStatusTone[application.status] ?? "neutral"}>{application.status}</Badge>
            </div>
            <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <CalendarClock className="h-3 w-3" /> Submitted {formatDate(application.submittedAt)}
              </span>
              {application.desiredMoveIn && <span>Move-in {formatDate(application.desiredMoveIn)}</span>}
            </p>
            {application.message && (
              <p className="mt-2 max-w-xl text-xs text-slate-500 dark:text-slate-400">“{application.message}”</p>
            )}
          </div>

          {application.status === "SUBMITTED" && (
            <Button
              size="sm"
              variant="outline"
              loading={withdrawingId === application.id}
              onClick={() => handleWithdraw(application.id)}
            >
              Withdraw
            </Button>
          )}
        </Card>
      ))}

      <Toast toast={toast} />
    </div>
  );
}
