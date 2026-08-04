import { BookingsTable } from "@/components/admin/BookingsTable";
import { bookings } from "@/data/bookings";

export default function AdminBookingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900 dark:text-white">Bookings</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Track and manage every reservation across hotels, villas and houses.
        </p>
      </div>
      <BookingsTable bookings={bookings} />
    </div>
  );
}
