export const bookingStatusTone = {
  confirmed: "success",
  pending: "warning",
  cancelled: "danger",
  completed: "primary",
} as const;

export const paymentStatusTone = {
  paid: "success",
  unpaid: "warning",
  refunded: "neutral",
} as const;

export const listingStateTone = {
  DRAFT: "neutral",
  EVIDENCE_PENDING: "warning",
  REVIEW: "primary",
  PUBLISHED: "success",
  PAUSED: "warning",
  SUSPENDED: "danger",
  WITHDRAWN: "neutral",
  ARCHIVED: "neutral",
} as const;

export const listingStateLabel = {
  DRAFT: "Draft",
  EVIDENCE_PENDING: "Evidence Pending",
  REVIEW: "In Review",
  PUBLISHED: "Published",
  PAUSED: "Paused",
  SUSPENDED: "Suspended",
  WITHDRAWN: "Withdrawn",
  ARCHIVED: "Archived",
} as const;

export const applicationStatusTone = {
  SUBMITTED: "warning",
  WITHDRAWN: "neutral",
  DECIDED: "success",
} as const;

export const offerStatusTone = {
  DRAFT: "neutral",
  SENT: "warning",
  ACCEPTED: "success",
  DECLINED: "danger",
  EXPIRED: "neutral",
  WITHDRAWN: "neutral",
} as const;

export const agreementStatusTone = {
  DRAFT: "neutral",
  SENT: "warning",
  SIGNED: "success",
  VOID: "danger",
} as const;

export const occupancyStatusTone = {
  PENDING_MOVE_IN: "warning",
  ACTIVE: "success",
  ENDED: "neutral",
} as const;

export const obligationStatusTone = {
  PENDING: "warning",
  PARTIALLY_PAID: "warning",
  PAID: "success",
  WAIVED: "neutral",
  FAILED: "danger",
  REFUNDED: "neutral",
} as const;

// Distinct from the legacy `paymentStatusTone` above (which covers the old
// short-stay Payment.status values paid/unpaid/refunded).
export const simulatedPaymentStatusTone = {
  PENDING: "warning",
  SUCCEEDED: "success",
  FAILED: "danger",
} as const;

export const depositStatusTone = {
  HELD: "warning",
  RELEASED: "success",
  FORFEITED: "danger",
  PARTIALLY_RELEASED: "warning",
} as const;

export const payoutStatusTone = {
  PENDING: "warning",
  PAID: "success",
  FAILED: "danger",
  HELD: "danger",
} as const;

export const refundStatusTone = {
  REQUESTED: "warning",
  APPROVED: "primary",
  REJECTED: "danger",
  COMPLETED: "success",
} as const;

export const disputeStatusTone = {
  OPEN: "warning",
  RESOLVED: "success",
  REJECTED: "danger",
} as const;

export const reconciliationStatusTone = {
  CLEAN: "success",
  DISCREPANCIES_FOUND: "danger",
} as const;

// --- USER account surface ---

export const identityStatusTone = {
  not_submitted: "neutral",
  pending: "warning",
  verified: "success",
  rejected: "danger",
  expired: "danger",
  additional_evidence_required: "warning",
} as const;

export const identityStatusLabel = {
  not_submitted: "Not Verified",
  pending: "Verification Pending",
  verified: "Identity Verified",
  rejected: "Verification Rejected",
  expired: "Verification Expired",
  additional_evidence_required: "More Evidence Needed",
} as const;

export const subletRequestStatusTone = {
  pending_verification: "warning",
  pending_admin_review: "warning",
  approved: "success",
  rejected: "danger",
} as const;

export const subletRequestStatusLabel = {
  pending_verification: "Pending Verification",
  pending_admin_review: "Pending Admin Review",
  approved: "Approved",
  rejected: "Rejected",
} as const;
