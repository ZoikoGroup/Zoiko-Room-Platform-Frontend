import { TrustSafetyManager } from "@/components/admin/TrustSafetyManager";
import { requireSuperAdmin } from "@/lib/api";

export default async function AdminTrustSafetyPage() {
  await requireSuperAdmin();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900 dark:text-white">Trust &amp; Safety</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Manage market releases, verify provider authority, and resolve occupancy classification — the checks every listing must clear before it can publish.
        </p>
      </div>
      <TrustSafetyManager />
    </div>
  );
}
