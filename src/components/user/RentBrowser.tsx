"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import Link from "next/link";
import { Bath, BedDouble, MapPin, Ruler, Search, Send, Users } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Loader } from "@/components/ui/Loader";
import { PublicListing } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { errorMessage, listPublicListings, listRentalApplications, submitRentalApplication } from "@/lib/user-api";
import { IdentityGate } from "@/components/user/IdentityGate";
import { useUserSession } from "@/components/user/UserSessionContext";
import { Card, EmptyState, Field, Toast, inputClass, useToast } from "@/components/user/ui";

export function RentBrowser() {
  const { identityVerified } = useUserSession();
  const { toast, showToast } = useToast();

  const [listings, setListings] = useState<PublicListing[]>([]);
  const [appliedListingIds, setAppliedListingIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  const [selected, setSelected] = useState<PublicListing | null>(null);
  const [message, setMessage] = useState("");
  const [desiredMoveIn, setDesiredMoveIn] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([listPublicListings(), listRentalApplications().catch(() => [])])
      .then(([published, applications]) => {
        setListings(published);
        setAppliedListingIds(
          new Set(applications.filter((a) => a.status !== "WITHDRAWN").map((a) => a.listingId))
        );
      })
      .catch(() => showToast("Could not load available rooms right now.", "error"))
      .finally(() => setLoading(false));
  }, [showToast]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return listings;
    return listings.filter((l) =>
      [l.name, l.city, l.location, l.roomType].some((field) => field.toLowerCase().includes(q))
    );
  }, [listings, query]);

  function openApply(listing: PublicListing) {
    setSelected(listing);
    setMessage("");
    setDesiredMoveIn("");
    setError("");
  }

  async function handleApply(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setError("");
    setSubmitting(true);
    try {
      await submitRentalApplication({
        listingId: selected.id,
        message: message.trim(),
        desiredMoveIn: desiredMoveIn || null,
      });
      setAppliedListingIds((prev) => new Set(prev).add(selected.id));
      setSelected(null);
      showToast("Application submitted. Track it under My Applications.");
    } catch (err) {
      setError(errorMessage(err, "Could not submit your application."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-5">
      <IdentityGate action="apply for a room">
        <Card className="!bg-emerald-50 !ring-emerald-200 dark:!bg-emerald-500/10 dark:!ring-emerald-500/20">
          <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">
            Your identity is verified — you can apply to any room below.
          </p>
        </Card>
      </IdentityGate>

      <div className="flex items-center gap-2 rounded-full bg-white px-4 py-2.5 shadow-sm ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-white/10">
        <Search className="h-4 w-4 shrink-0 text-slate-400" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by room name, city or area..."
          className="w-full bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400 dark:text-slate-200"
        />
      </div>

      {loading ? (
        <Loader label="Loading available rooms" />
      ) : filtered.length === 0 ? (
        <Card>
          <EmptyState
            message={
              listings.length === 0
                ? "No rooms are published yet. Check back once hosts publish their listings."
                : "No rooms match that search."
            }
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((listing) => {
            const applied = appliedListingIds.has(listing.id);
            return (
              <div
                key={listing.id}
                className="flex flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg dark:bg-slate-900 dark:ring-white/10"
              >
                {listing.images[0] ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img src={listing.images[0]} alt={listing.name} className="h-44 w-full object-cover" />
                ) : (
                  <div className="flex h-44 w-full items-center justify-center bg-primary-50 dark:bg-primary-500/10">
                    <BedDouble className="h-8 w-8 text-primary-300" />
                  </div>
                )}

                <div className="flex flex-1 flex-col p-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-heading text-sm font-bold text-primary-900 dark:text-white">{listing.name}</p>
                    <Badge tone="primary">{listing.roomType}</Badge>
                  </div>

                  <p className="mt-1 flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                    <MapPin className="h-3.5 w-3.5" /> {listing.location}, {listing.city}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
                    <span className="flex items-center gap-1">
                      <Users className="h-3.5 w-3.5" /> {listing.guests} guest{listing.guests === 1 ? "" : "s"}
                    </span>
                    <span className="flex items-center gap-1">
                      <Bath className="h-3.5 w-3.5" /> {listing.bathrooms}
                    </span>
                    {listing.size > 0 && (
                      <span className="flex items-center gap-1">
                        <Ruler className="h-3.5 w-3.5" /> {listing.size} sq ft
                      </span>
                    )}
                  </div>

                  {listing.description && (
                    <p className="mt-3 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
                      {listing.description}
                    </p>
                  )}

                  <div className="mt-auto flex items-end justify-between gap-2 pt-4">
                    <div>
                      <p className="font-heading text-lg font-extrabold text-primary-900 dark:text-white">
                        {formatCurrency(listing.pricePerNight)}
                        <span className="text-xs font-medium text-slate-400"> / night</span>
                      </p>
                      <p className="text-xs text-slate-400">Min. {listing.minStayNights} nights</p>
                    </div>
                    <Button
                      size="sm"
                      variant={applied ? "outline" : "primary"}
                      disabled={!identityVerified || applied}
                      onClick={() => openApply(listing)}
                    >
                      {applied ? "Applied" : "Apply"}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <Modal open={Boolean(selected)} onClose={() => setSelected(null)} title={`Apply for ${selected?.name ?? ""}`}>
        <form onSubmit={handleApply} className="space-y-4">
          <div className="rounded-xl bg-slate-50 px-4 py-3 text-xs text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
            <p>
              {selected?.location}, {selected?.city} — {selected ? formatCurrency(selected.pricePerNight) : ""} / night,
              minimum {selected?.minStayNights} nights.
            </p>
            <p className="mt-1">Host contact: {selected?.ownerName || "Zoiko host"}</p>
          </div>

          <Field label="Desired move-in date">
            <input
              type="date"
              value={desiredMoveIn}
              onChange={(e) => setDesiredMoveIn(e.target.value)}
              className={inputClass}
            />
          </Field>

          <Field label="Message to the host" hint="Tell the host a little about yourself and your stay.">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
              placeholder="I'm relocating for work and looking for a 6-month stay..."
              className={inputClass}
            />
          </Field>

          {error && (
            <p className="rounded-lg bg-accent-50 px-3 py-2 text-xs font-medium text-accent-700 ring-1 ring-accent-200">
              {error}
            </p>
          )}

          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setSelected(null)}>
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              <Send className="h-4 w-4" /> Submit application
            </Button>
          </div>
        </form>
      </Modal>

      <p className="text-center text-xs text-slate-400">
        Already applied somewhere?{" "}
        <Link href="/account/applications" className="font-semibold text-primary-700 dark:text-primary-300">
          Track your applications
        </Link>
      </p>

      <Toast toast={toast} />
    </div>
  );
}
