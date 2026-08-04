import { Payment } from "@/lib/types";
import { bookings } from "./bookings";

const methods: Payment["method"][] = ["Credit Card", "UPI", "Net Banking", "PayPal", "Wallet"];

export const payments: Payment[] = bookings
  .filter((b) => b.paymentStatus !== "unpaid" || b.status !== "cancelled")
  .map((b, i) => ({
    id: `PAY-${7000 + i}`,
    bookingId: b.id,
    guestName: b.guestName,
    amount: b.totalAmount,
    method: methods[i % methods.length],
    status: b.paymentStatus,
    date: b.createdAt,
  }));
