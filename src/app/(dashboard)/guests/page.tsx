import { GuestsTable } from "@/components/admin/GuestsTable";
import { guests } from "@/data/guests";

export default function AdminGuestsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900">Guests</h1>
        <p className="mt-1 text-sm text-slate-500">View guest profiles, booking history and spend.</p>
      </div>
      <GuestsTable guests={guests} />
    </div>
  );
}
