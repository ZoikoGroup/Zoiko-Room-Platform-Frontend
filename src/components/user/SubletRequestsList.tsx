"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CalendarClock, Repeat } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { SubletRequest } from "@/lib/types";
import { subletRequestStatusLabel, subletRequestStatusTone } from "@/lib/status";
import { formatDate } from "@/lib/utils";
import { errorMessage, listSubletRequests } from "@/lib/user-api";
import { Card, EmptyState, Toast, useToast } from "@/components/user/ui";

export function SubletRequestsList() {
  const { toast, showToast } = useToast();
  const [requests, setRequests] = useState<SubletRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listSubletRequests()
      .then(setRequests)
      .catch((err) => showToast(errorMessage(err, "Could not load your sublet requests."), "error"))
      .finally(() => setLoading(false));
  }, [showToast]);

  if (loading) return <Loader label="Loading your sublet requests" />;

  if (requests.length === 0) {
    return (
      <Card>
        <div className="flex flex-col items-center gap-4 py-10 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-300">
            <Repeat className="h-6 w-6" />
          </span>
          <EmptyState message="You have not requested to sublet any of your rentals." />
          <Link href="/account/rentals">
            <Button size="sm" variant="outline">
              Go to My Rentals
            </Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {requests.map((request) => (
        <Card key={request.id} className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="font-heading text-sm font-bold text-primary-900 dark:text-white">
              Occupancy #{request.currentOccupancyId}
            </p>
            <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <CalendarClock className="h-3 w-3" /> Requested {formatDate(request.createdAt)}
              </span>
              <span>Proposed renter party #{request.proposedRenterPartyId}</span>
              {request.decidedAt && <span>Decided {formatDate(request.decidedAt)}</span>}
            </p>
            {request.adminNotes && (
              <p className="mt-2 max-w-xl text-xs text-slate-500 dark:text-slate-400">
                Reviewer notes: {request.adminNotes}
              </p>
            )}
          </div>
          <Badge tone={subletRequestStatusTone[request.status] ?? "neutral"}>
            {subletRequestStatusLabel[request.status] ?? request.status}
          </Badge>
        </Card>
      ))}

      <Toast toast={toast} />
    </div>
  );
}
