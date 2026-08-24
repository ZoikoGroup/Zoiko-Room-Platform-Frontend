import { HostingPropertiesManager } from "@/components/user/HostingPropertiesManager";

export default function HostPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900 dark:text-white">Host a room</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Register the property you own, add the rooms inside it, then turn a room into a listing.
        </p>
      </div>
      <HostingPropertiesManager />
    </div>
  );
}
