import { Booking } from "@/lib/types";
import { guests } from "./guests";
import { listings } from "./listings";

function guestAvatar(name: string) {
  return guests.find((g) => g.name === name)?.avatar ?? "";
}

function nightsBetween(checkIn: string, checkOut: string) {
  const ms = new Date(checkOut).getTime() - new Date(checkIn).getTime();
  return Math.max(1, Math.round(ms / (1000 * 60 * 60 * 24)));
}

function findListing(id: string) {
  const listing = listings.find((l) => l.id === id)!;
  return listing;
}

const raw: Array<{
  id: string;
  listingId: string;
  guestName: string;
  guestEmail: string;
  checkIn: string;
  checkOut: string;
  guests: number;
  status: Booking["status"];
  paymentStatus: Booking["paymentStatus"];
  createdAt: string;
}> = [
  { id: "BK-24001", listingId: "L-1001", guestName: "Aarav Mehta", guestEmail: "aarav.mehta@example.com", checkIn: "2026-08-10", checkOut: "2026-08-13", guests: 2, status: "confirmed", paymentStatus: "paid", createdAt: "2026-07-28" },
  { id: "BK-24002", listingId: "L-2001", guestName: "Sneha Iyer", guestEmail: "sneha.iyer@example.com", checkIn: "2026-08-15", checkOut: "2026-08-19", guests: 6, status: "confirmed", paymentStatus: "paid", createdAt: "2026-07-30" },
  { id: "BK-24003", listingId: "L-3002", guestName: "Priya Nair", guestEmail: "priya.nair@example.com", checkIn: "2026-09-01", checkOut: "2026-09-04", guests: 5, status: "pending", paymentStatus: "unpaid", createdAt: "2026-08-01" },
  { id: "BK-24004", listingId: "L-1004", guestName: "Isha Kapoor", guestEmail: "isha.kapoor@example.com", checkIn: "2026-08-05", checkOut: "2026-08-07", guests: 3, status: "completed", paymentStatus: "paid", createdAt: "2026-07-20" },
  { id: "BK-24005", listingId: "L-2002", guestName: "Karan Malhotra", guestEmail: "karan.malhotra@example.com", checkIn: "2026-08-20", checkOut: "2026-08-23", guests: 8, status: "confirmed", paymentStatus: "paid", createdAt: "2026-08-02" },
  { id: "BK-24006", listingId: "L-1002", guestName: "Ananya Rao", guestEmail: "ananya.rao@example.com", checkIn: "2026-07-25", checkOut: "2026-07-27", guests: 2, status: "completed", paymentStatus: "paid", createdAt: "2026-07-10" },
  { id: "BK-24007", listingId: "L-3001", guestName: "Meera Pillai", guestEmail: "meera.pillai@example.com", checkIn: "2026-08-28", checkOut: "2026-09-01", guests: 4, status: "confirmed", paymentStatus: "paid", createdAt: "2026-08-03" },
  { id: "BK-24008", listingId: "L-1003", guestName: "Vikram Singh", guestEmail: "vikram.singh@example.com", checkIn: "2026-08-12", checkOut: "2026-08-13", guests: 2, status: "cancelled", paymentStatus: "refunded", createdAt: "2026-07-29" },
  { id: "BK-24009", listingId: "L-2003", guestName: "Rohan Verma", guestEmail: "rohan.verma@example.com", checkIn: "2026-09-10", checkOut: "2026-09-15", guests: 10, status: "pending", paymentStatus: "unpaid", createdAt: "2026-08-03" },
  { id: "BK-24010", listingId: "L-1001", guestName: "Aditya Kulkarni", guestEmail: "aditya.kulkarni@example.com", checkIn: "2026-07-18", checkOut: "2026-07-20", guests: 2, status: "completed", paymentStatus: "paid", createdAt: "2026-07-05" },
  { id: "BK-24011", listingId: "L-3002", guestName: "Priya Nair", guestEmail: "priya.nair@example.com", checkIn: "2026-06-14", checkOut: "2026-06-17", guests: 4, status: "completed", paymentStatus: "paid", createdAt: "2026-06-01" },
  { id: "BK-24012", listingId: "L-2001", guestName: "Sneha Iyer", guestEmail: "sneha.iyer@example.com", checkIn: "2026-05-02", checkOut: "2026-05-05", guests: 5, status: "completed", paymentStatus: "paid", createdAt: "2026-04-18" },
  { id: "BK-24013", listingId: "L-1004", guestName: "Aarav Mehta", guestEmail: "aarav.mehta@example.com", checkIn: "2026-08-22", checkOut: "2026-08-24", guests: 2, status: "confirmed", paymentStatus: "paid", createdAt: "2026-08-02" },
  { id: "BK-24014", listingId: "L-3001", guestName: "Isha Kapoor", guestEmail: "isha.kapoor@example.com", checkIn: "2026-09-05", checkOut: "2026-09-07", guests: 3, status: "pending", paymentStatus: "unpaid", createdAt: "2026-08-03" },
  { id: "BK-24015", listingId: "L-1002", guestName: "Meera Pillai", guestEmail: "meera.pillai@example.com", checkIn: "2026-04-10", checkOut: "2026-04-12", guests: 2, status: "completed", paymentStatus: "paid", createdAt: "2026-03-28" },
];

export const bookings: Booking[] = raw.map((b) => {
  const listing = findListing(b.listingId);
  const nights = nightsBetween(b.checkIn, b.checkOut);
  return {
    id: b.id,
    listingId: b.listingId,
    listingName: listing.name,
    propertyType: listing.propertyType,
    guestName: b.guestName,
    guestEmail: b.guestEmail,
    guestAvatar: guestAvatar(b.guestName),
    checkIn: b.checkIn,
    checkOut: b.checkOut,
    nights,
    guests: b.guests,
    totalAmount: nights * listing.pricePerNight,
    status: b.status,
    paymentStatus: b.paymentStatus,
    createdAt: b.createdAt,
  };
});
