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
