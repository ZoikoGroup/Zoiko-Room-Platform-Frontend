// Private-room-only taxonomy per the marketplace standard -- whole-home, studio, hotel,
// nightly/vacation, hostel and dorm/shared-bed inventory is explicitly rejected.
export type PropertyType = "private_room";

export type ListingState =
  | "DRAFT"
  | "EVIDENCE_PENDING"
  | "REVIEW"
  | "PUBLISHED"
  | "PAUSED"
  | "SUSPENDED"
  | "WITHDRAWN"
  | "ARCHIVED";

export type BookingStatus = "confirmed" | "pending" | "cancelled" | "completed";
export type PaymentStatus = "paid" | "unpaid" | "refunded";
export type AdminRole = "admin" | "super_admin";
export type ApprovalStatus = "pending" | "approved" | "rejected";

export interface Listing {
  id: string;
  slug: string;
  name: string;
  propertyType: PropertyType;
  roomType: string;
  city: string;
  location: string;
  latitude?: number | null;
  longitude?: number | null;
  pricePerNight: number;
  rating: number;
  reviewCount: number;
  guests: number;
  bedrooms: number;
  bathrooms: number;
  size: number;
  images: string[];
  amenities: string[];
  description: string;
  tags: string[];
  featured?: boolean;
  ownerId: number;
  roomId: number | null;
  minStayNights: number;
  marketReleaseId: number | null;
  state: ListingState;
  contactName: string;
  contactPhone: string;
  contactEmail: string;
}

export interface PublishEligibility {
  eligible: boolean;
  reasons: string[];
}

export type PartyType = "provider" | "renter" | "institution" | "zoiko_operator";

export interface Party {
  id: number;
  partyType: PartyType;
  status: "active" | "suspended" | "closed";
  jurisdiction: string;
  createdAt: string;
}

export interface MarketRelease {
  id: number;
  jurisdiction: string;
  status: "draft" | "active" | "disabled";
  minStayNights: number;
  effectiveFrom: string | null;
  approvedAt: string | null;
  createdAt: string;
}

export interface Property {
  id: number;
  ownerPartyId: number;
  address: string;
  city: string;
  status: "active" | "inactive";
  createdAt: string;
}

export interface Room {
  id: number;
  propertyId: number;
  roomType: string;
  size: number;
  hasEnsuite: boolean;
  status: "active" | "inactive";
  createdAt: string;
}

export type AuthorityStatus =
  | "not_started"
  | "pending"
  | "verified"
  | "expiring"
  | "expired"
  | "failed"
  | "conflict"
  | "review_required";

export interface AuthorityRecord {
  id: number;
  partyId: number;
  roomId: number;
  authorityType: string;
  evidenceRef: string;
  verifiedAt: string | null;
  expiresAt: string | null;
  status: AuthorityStatus;
  createdAt: string;
}

export interface RoomPassportClaim {
  id: number;
  roomId: number;
  claimType: string;
  value: string;
  evidenceTier: string;
  verifiedAt: string | null;
  expiresAt: string | null;
  createdAt: string;
}

export type OccupancyReviewState = "UNKNOWN" | "UNSUPPORTED" | "APPROVED";

export interface OccupancyClassification {
  id: number;
  roomId: number;
  classification: string;
  confidence: number;
  evidenceRef: string;
  jurisdiction: string;
  ruleVersion: number;
  reviewState: OccupancyReviewState;
  updatedAt: string;
}

export interface Booking {
  id: string;
  listingId: string;
  listingName: string;
  propertyType: PropertyType;
  guestName: string;
  guestEmail: string;
  guestAvatar: string;
  checkIn: string;
  checkOut: string;
  nights: number;
  guests: number;
  totalAmount: number;
  status: BookingStatus;
  paymentStatus: PaymentStatus;
  createdAt: string;
}

export interface Guest {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar: string;
  location: string;
  totalBookings: number;
  totalSpent: number;
  joinedAt: string;
  status: "active" | "inactive";
}

export interface Review {
  id: string;
  listingId: string;
  listingName: string;
  guestName: string;
  guestAvatar: string;
  rating: number;
  comment: string;
  date: string;
  propertyType: PropertyType;
}

export interface Payment {
  id: string;
  bookingId: string;
  guestName: string;
  amount: number;
  method: "Credit Card" | "UPI" | "Net Banking" | "PayPal" | "Wallet";
  status: PaymentStatus;
  date: string;
}

export interface AdminUserSummary {
  id: number;
  email: string;
  fullName: string;
  phone: string;
  role: AdminRole;
  isActive: boolean;
  approvalStatus: ApprovalStatus;
  createdAt: string;
}

export interface SearchResult {
  id: string;
  type: "listing" | "guest" | "booking";
  title: string;
  subtitle: string;
  href: string;
}

// --- Leasing pipeline (application -> offer -> agreement) ---

export type ApplicationStatus = "SUBMITTED" | "WITHDRAWN" | "DECIDED";

export interface ApplicationDecisionRecord {
  id: number;
  decision: "APPROVED" | "REJECTED";
  reasonCode: string;
  note: string;
  decidedByAdminId: number;
  decidedAt: string;
}

export type OfferStatus = "DRAFT" | "SENT" | "ACCEPTED" | "DECLINED" | "EXPIRED" | "WITHDRAWN";

export interface OfferTermsRecord {
  id: number;
  version: number;
  monthlyRent: number;
  depositAmount: number;
  startDate: string;
  termMonths: number;
  createdAt: string;
}

export type AgreementStatus = "DRAFT" | "SENT" | "SIGNED" | "VOID";

export interface Agreement {
  id: number;
  offerId: number;
  version: number;
  status: AgreementStatus;
  contentRef: string;
  signedByProviderAt: string | null;
  signedByRenterAt: string | null;
  signatureRef: string;
  createdAt: string;
}

export interface Offer {
  id: number;
  applicationId: number;
  listingId: string;
  guestId: string;
  status: OfferStatus;
  currentVersion: number;
  createdAt: string;
  terms: OfferTermsRecord[];
  agreement: Agreement | null;
}

export interface Application {
  id: number;
  listingId: string;
  guestId: string;
  guestName: string;
  guestEmail: string;
  status: ApplicationStatus;
  message: string;
  desiredMoveIn: string | null;
  submittedAt: string;
  updatedAt: string;
  decisions: ApplicationDecisionRecord[];
  offer: Offer | null;
}

// --- Occupancy ---

export type OccupancyStatus = "PENDING_MOVE_IN" | "ACTIVE" | "ENDED";

export interface Occupancy {
  id: number;
  offerId: number;
  listingId: string;
  roomId: number;
  guestId: string;
  guestName: string;
  status: OccupancyStatus;
  moveInDate: string | null;
  expectedEndDate: string | null;
  moveOutDate: string | null;
  createdAt: string;
  endedAt: string | null;
}

// --- Finance ledger ---

export type ObligationType = "RENT" | "DEPOSIT" | "FEE" | "TAX";
export type MoneyPlane = "OCCUPANCY" | "SAFEGUARDED" | "REVENUE";
export type ObligationStatus = "PENDING" | "PARTIALLY_PAID" | "PAID" | "WAIVED" | "FAILED" | "REFUNDED";

export interface Obligation {
  id: number;
  obligationType: ObligationType;
  moneyPlane: MoneyPlane;
  amount: number;
  currency: string;
  dueDate: string;
  status: ObligationStatus;
  guestId: string;
  agreementId: number | null;
  occupancyId: number | null;
  payoutId: number | null;
  createdAt: string;
}

export type SimulatedPaymentStatus = "PENDING" | "SUCCEEDED" | "FAILED";

export interface PaymentAllocation {
  id: number;
  paymentId: number;
  obligationId: number;
  amountAllocated: number;
  createdAt: string;
}

export interface SimulatedPayment {
  id: number;
  guestId: string;
  amount: number;
  currency: string;
  idempotencyKey: string;
  status: SimulatedPaymentStatus;
  createdAt: string;
  confirmedAt: string | null;
  allocations: PaymentAllocation[];
}

export type DepositStatus = "HELD" | "RELEASED" | "FORFEITED" | "PARTIALLY_RELEASED";

export interface DepositRecord {
  id: number;
  obligationId: number;
  status: DepositStatus;
  heldAmount: number;
  releasedAmount: number;
  releasedAt: string | null;
  notes: string;
}

export type PayoutStatus = "PENDING" | "PAID" | "FAILED" | "HELD";

export interface PayoutRecord {
  id: number;
  partyId: number;
  periodKey: string;
  amount: number;
  currency: string;
  status: PayoutStatus;
  holdReason: string;
  createdAt: string;
  paidAt: string | null;
}

export type RefundStatus = "REQUESTED" | "APPROVED" | "REJECTED" | "COMPLETED";

export interface RefundRequest {
  id: number;
  paymentId: number;
  obligationId: number;
  amount: number;
  reason: string;
  status: RefundStatus;
  requestedByAdminId: number;
  decidedByAdminId: number | null;
  createdAt: string;
  decidedAt: string | null;
}

export type DisputeCategory = "CHARGEBACK" | "COMPENSATION" | "OTHER";
export type DisputeStatus = "OPEN" | "RESOLVED" | "REJECTED";

export interface DisputeCase {
  id: number;
  paymentId: number | null;
  occupancyId: number | null;
  category: DisputeCategory;
  description: string;
  status: DisputeStatus;
  openedAt: string;
  resolvedAt: string | null;
  resolutionNotes: string;
}

export type ReconciliationStatus = "CLEAN" | "DISCREPANCIES_FOUND";

export interface ReconciliationRun {
  id: number;
  runAt: string;
  totals: Record<string, number>;
  mismatches: string[];
  status: ReconciliationStatus;
}
