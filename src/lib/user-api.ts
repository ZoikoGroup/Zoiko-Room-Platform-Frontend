import { ApiError, apiClientFetch } from "@/lib/api-client";
import {
  HostedListing,
  IdentityDocumentType,
  IdentityVerificationRecord,
  Property,
  PublicListing,
  PublishEligibility,
  Room,
  SimulatedPayment,
  SubletRequest,
  UserApplication,
  UserOccupancy,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Typed clients for the USER-facing backend surface. Every path here is an endpoint
 * that already exists on the FastAPI app -- nothing is invented. Auth is the
 * `zoiko_user_token` cookie, sent automatically by `apiClientFetch`.
 */

/** Pulls a readable message out of whatever the API layer threw. */
export function errorMessage(err: unknown, fallback = "Something went wrong. Please try again."): string {
  if (err instanceof ApiError) return err.message || fallback;
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}

// --- Identity verification -------------------------------------------------

/** Submits a real uploaded document -- this is a multipart request, not JSON, so
 *  apiClientFetch is told to let the browser set its own multipart boundary. */
export function submitIdentityVerification(payload: {
  documentType: IdentityDocumentType;
  file: File;
  documentNumber?: string;
  customDocumentName?: string;
}): Promise<IdentityVerificationRecord> {
  const form = new FormData();
  form.append("document_type", payload.documentType);
  form.append("document_number", payload.documentNumber ?? "");
  form.append("custom_document_name", payload.customDocumentName ?? "");
  form.append("file", payload.file);
  return apiClientFetch<IdentityVerificationRecord>("/api/users/identity-verifications", {
    method: "POST",
    body: form,
  });
}

export function listIdentityVerifications(): Promise<IdentityVerificationRecord[]> {
  return apiClientFetch<IdentityVerificationRecord[]>("/api/users/identity-verifications");
}

export function getIdentityVerification(verificationId: number): Promise<IdentityVerificationRecord> {
  return apiClientFetch<IdentityVerificationRecord>(`/api/users/identity-verifications/${verificationId}`);
}

/** Opens/downloads the caller's own uploaded document. The backend enforces
 *  ownership by party_id -- this URL 403s for anyone else's verification, so it's
 *  safe to build client-side with nothing but the verification id. */
export function identityDocumentUrl(verificationId: number): string {
  return `${API_URL}/api/users/identity-verifications/${verificationId}/document`;
}

/** True when at least one submitted document has been approved by a super admin. */
export function hasVerifiedIdentity(records: IdentityVerificationRecord[]): boolean {
  return records.some((record) => record.status === "verified");
}

// --- Renting ---------------------------------------------------------------

/** Public catalogue of PUBLISHED listings -- the inventory a user can apply to. */
export function listPublicListings(): Promise<PublicListing[]> {
  return apiClientFetch<PublicListing[]>("/api/public/listings");
}

export function submitRentalApplication(payload: {
  listingId: string;
  message?: string;
  desiredMoveIn?: string | null;
}): Promise<UserApplication> {
  return apiClientFetch<UserApplication>("/api/users/rentals/applications", {
    method: "POST",
    body: JSON.stringify({ message: "", desiredMoveIn: null, ...payload }),
  });
}

export function listRentalApplications(): Promise<UserApplication[]> {
  return apiClientFetch<UserApplication[]>("/api/users/rentals/applications");
}

export function getRentalApplication(applicationId: number): Promise<UserApplication> {
  return apiClientFetch<UserApplication>(`/api/users/rentals/applications/${applicationId}`);
}

export function withdrawRentalApplication(applicationId: number): Promise<UserApplication> {
  return apiClientFetch<UserApplication>(`/api/users/rentals/applications/${applicationId}/withdraw`, {
    method: "POST",
  });
}

export function listOccupancies(): Promise<UserOccupancy[]> {
  return apiClientFetch<UserOccupancy[]>("/api/users/rentals/occupancies");
}

export function getOccupancy(occupancyId: number): Promise<UserOccupancy> {
  return apiClientFetch<UserOccupancy>(`/api/users/rentals/occupancies/${occupancyId}`);
}

export function submitSubletRequest(
  occupancyId: number,
  payload: { proposedRenterPartyId: number; authorityEvidenceRef?: string }
): Promise<SubletRequest> {
  return apiClientFetch<SubletRequest>(`/api/users/rentals/occupancies/${occupancyId}/sublet-request`, {
    method: "POST",
    // The backend rejects the request unless occupancyId in the body matches the path.
    body: JSON.stringify({ occupancyId, authorityEvidenceRef: "", ...payload }),
  });
}

export function listSubletRequests(): Promise<SubletRequest[]> {
  return apiClientFetch<SubletRequest[]>("/api/users/rentals/sublet-requests");
}

// --- Hosting ---------------------------------------------------------------

export function listHostedProperties(): Promise<Property[]> {
  return apiClientFetch<Property[]>("/api/users/hosting/properties");
}

export function createHostedProperty(payload: { address: string; city: string }): Promise<Property> {
  return apiClientFetch<Property>("/api/users/hosting/properties", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateHostedProperty(
  propertyId: number,
  payload: { address: string; city: string }
): Promise<Property> {
  return apiClientFetch<Property>(`/api/users/hosting/properties/${propertyId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function listHostedRooms(propertyId: number): Promise<Room[]> {
  return apiClientFetch<Room[]>(`/api/users/hosting/properties/${propertyId}/rooms`);
}

export function createHostedRoom(
  propertyId: number,
  payload: { size: number; hasEnsuite: boolean }
): Promise<Room> {
  return apiClientFetch<Room>(`/api/users/hosting/properties/${propertyId}/rooms`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateHostedRoom(
  propertyId: number,
  roomId: number,
  payload: { size: number; hasEnsuite: boolean }
): Promise<Room> {
  return apiClientFetch<Room>(`/api/users/hosting/properties/${propertyId}/rooms/${roomId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export interface HostedListingInput {
  name: string;
  roomType: string;
  city: string;
  location: string;
  pricePerNight: number;
  guests: number;
  bedrooms: number;
  bathrooms: number;
  size: number;
  description: string;
  amenities: string[];
  images: string[];
  minStayNights: number;
  roomId: number;
  contactName: string;
  contactPhone: string;
  contactEmail: string;
}

export function createHostedListing(payload: HostedListingInput): Promise<HostedListing> {
  return apiClientFetch<HostedListing>("/api/users/hosting/listings", {
    method: "POST",
    // Whole-home / nightly inventory is rejected platform-wide, so propertyType is fixed.
    body: JSON.stringify({ propertyType: "private_room", tags: [], featured: false, ...payload }),
  });
}

export function updateHostedListing(
  listingId: string,
  payload: Partial<HostedListingInput>
): Promise<HostedListing> {
  return apiClientFetch<HostedListing>(`/api/users/hosting/listings/${listingId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function getHostedListingPublishEligibility(listingId: string): Promise<PublishEligibility> {
  return apiClientFetch<PublishEligibility>(`/api/users/hosting/listings/${listingId}/publish-eligibility`);
}

export function publishHostedListing(listingId: string): Promise<HostedListing> {
  return apiClientFetch<HostedListing>(`/api/users/hosting/listings/${listingId}/publish`, {
    method: "POST",
  });
}

// --- Payments --------------------------------------------------------------

export function listUserPayments(): Promise<SimulatedPayment[]> {
  return apiClientFetch<SimulatedPayment[]>("/api/users/payments");
}

// --- Hosted-listing local index --------------------------------------------
//
// The backend exposes create / update / publish-eligibility / publish for hosted
// listings but no "list my listings" endpoint, so there is nothing to read a host's
// drafts back from. We keep the full ListingRead the API hands back on every write
// in localStorage (per user id) so drafts survive a reload, and merge the published
// ones back in from /api/public/listings. Drafts created on another device will not
// appear until a GET endpoint exists.

const HOSTED_LISTINGS_KEY = "zoiko_user_hosted_listings";

function hostedListingsKey(userId: number): string {
  return `${HOSTED_LISTINGS_KEY}:${userId}`;
}

export function readCachedHostedListings(userId: number): HostedListing[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(hostedListingsKey(userId));
    const parsed: unknown = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? (parsed as HostedListing[]) : [];
  } catch {
    return [];
  }
}

export function cacheHostedListing(userId: number, listing: HostedListing): HostedListing[] {
  const next = [listing, ...readCachedHostedListings(userId).filter((l) => l.id !== listing.id)];
  try {
    window.localStorage.setItem(hostedListingsKey(userId), JSON.stringify(next));
  } catch {
    // A full or disabled localStorage must not break the write that just succeeded.
  }
  return next;
}

/** Published listings the user hosts, recovered from the public catalogue by contact email. */
export function toHostedListing(listing: PublicListing): HostedListing {
  return {
    ...listing,
    ownerId: null,
    state: "PUBLISHED",
    marketReleaseId: null,
    contactName: listing.ownerName,
    contactPhone: listing.ownerPhone,
    contactEmail: listing.ownerEmail,
  };
}
