import { PropertiesManager } from "@/components/admin/PropertiesManager";
import { listings } from "@/data/listings";

export default function AdminPropertiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900 dark:text-white">Properties &amp; Rooms</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Manage hotel rooms, villas and houses, update availability and pricing.
        </p>
      </div>
      <PropertiesManager initialListings={listings} />
    </div>
  );
}
