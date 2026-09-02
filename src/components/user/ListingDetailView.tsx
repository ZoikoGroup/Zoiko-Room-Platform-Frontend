"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ArrowLeft, Bath, BedDouble, MapPin, Ruler, Users } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { StarRating } from "@/components/ui/StarRating";
import { PublicListing } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { errorMessage, getPublicListing, listRentalApplications } from "@/lib/user-api";
import { ApplyForRoomModal } from "@/components/user/ApplyForRoomModal";
import { ListingImageGallery } from "@/components/user/ListingImageGallery";
import { IdentityGate } from "@/components/user/IdentityGate";
import { Card, EmptyState, Toast, useToast } from "@/components/user/ui";

export function ListingDetailView({ listingId }: { listingId: string }) {
  const { toast, showToast } = useToast();

  const [listing, setListing] = useState<PublicListing | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [applied, setApplied] = useState(false);
  const [applying, setApplying] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError("");
    try {
      const [found, applications] = await Promise.all([
        getPublicListing(listingId),
        listRentalApplications().catch(() => []),
      ]);
      setListing(found);
      setApplied(applications.some((a) => a.listingId === listingId));
    } catch (err) {
      setLoadError(errorMessage(err, "This listing could not be found. It may have been withdrawn or unpublished."));
    } finally {
      setLoading(false);
    }
  }, [listingId]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return <Loader label="Loading listing" />;

  if (loadError || !listing) {
    return (
      <div className="space-y-4">
        <Link href="/account/rent" className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary-700 dark:text-primary-300">
          <ArrowLeft className="h-4 w-4" /> Back to Find a Room
        </Link>
        <Card>
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <AlertTriangle className="h-6 w-6 text-accent-600" />
            <EmptyState message={loadError || "This listing is no longer available."} />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <Link href="/account/rent" className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary-700 dark:text-primary-300">
        <ArrowLeft className="h-4 w-4" /> Back to Find a Room
      </Link>

      <ListingImageGallery images={listing.images} alt={listing.name} />

      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="font-heading text-xl font-extrabold text-primary-900 dark:text-white">{listing.name}</h1>
            <Badge tone="primary">{listing.roomType}</Badge>
          </div>
          <p className="mt-1 flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
            <MapPin className="h-4 w-4" /> {listing.location}, {listing.city}
          </p>
          {listing.reviewCount > 0 && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <StarRating rating={listing.rating} size={14} />
              <span className="text-xs text-slate-400">
                {listing.rating.toFixed(1)} ({listing.reviewCount} review{listing.reviewCount === 1 ? "" : "s"})
              </span>
            </div>
          )}
        </div>

        <div className="shrink-0 text-right">
          <p className="font-heading text-2xl font-extrabold text-primary-900 dark:text-white">
            {formatCurrency(listing.pricePerNight, listing.currency)}
            <span className="text-sm font-medium text-slate-400"> / night</span>
          </p>
          <p className="text-xs text-slate-400">Minimum stay {listing.minStayNights} nights</p>
        </div>
      </div>

      <Card>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <Users className="h-4 w-4 text-primary-600" /> {listing.guests} guest{listing.guests === 1 ? "" : "s"}
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <BedDouble className="h-4 w-4 text-primary-600" /> {listing.bedrooms} bedroom{listing.bedrooms === 1 ? "" : "s"}
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <Bath className="h-4 w-4 text-primary-600" /> {listing.bathrooms} bathroom{listing.bathrooms === 1 ? "" : "s"}
          </div>
          {listing.size > 0 && (
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
              <Ruler className="h-4 w-4 text-primary-600" /> {listing.size} sq ft
            </div>
          )}
        </div>
      </Card>

      {listing.description && (
        <Card>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Description</p>
          <p className="whitespace-pre-line text-sm text-slate-600 dark:text-slate-300">{listing.description}</p>
        </Card>
      )}

      {listing.amenities.length > 0 && (
        <Card>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Amenities</p>
          <div className="flex flex-wrap gap-2">
            {listing.amenities.map((amenity) => (
              <Badge key={amenity} tone="neutral">
                {amenity}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      <Card>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Host</p>
        <p className="text-sm text-slate-600 dark:text-slate-300">{listing.ownerName || "Zoiko host"}</p>
      </Card>

      <IdentityGate action="apply for a room">
        <Card className="!bg-emerald-50 !ring-emerald-200 dark:!bg-emerald-500/10 dark:!ring-emerald-500/20">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">
              Your identity is verified — you can apply for this room.
            </p>
            <Button disabled={applied} onClick={() => setApplying(true)}>
              {applied ? "Applied" : "Apply for this room"}
            </Button>
          </div>
        </Card>
      </IdentityGate>

      <ApplyForRoomModal
        listing={applying ? listing : null}
        onClose={() => setApplying(false)}
        onApplied={() => {
          setApplied(true);
          setApplying(false);
          showToast("Application submitted. Track it under My Applications.");
        }}
      />

      <Toast toast={toast} />
    </div>
  );
}
