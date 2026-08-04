import { CreditCard, RefreshCcw, Wallet } from "lucide-react";
import { StatCard } from "@/components/admin/StatCard";
import { PaymentsTable } from "@/components/admin/PaymentsTable";
import { payments } from "@/data/payments";
import { formatCurrency } from "@/lib/utils";

export default function AdminPaymentsPage() {
  const collected = payments.filter((p) => p.status === "paid").reduce((s, p) => s + p.amount, 0);
  const pending = payments.filter((p) => p.status === "unpaid").reduce((s, p) => s + p.amount, 0);
  const refunded = payments.filter((p) => p.status === "refunded").reduce((s, p) => s + p.amount, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900">Payments</h1>
        <p className="mt-1 text-sm text-slate-500">Track collections, pending dues and refunds.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Total Collected" value={formatCurrency(collected)} change="+9.2%" icon={Wallet} index={0} />
        <StatCard label="Pending Dues" value={formatCurrency(pending)} change="-3.1%" trend="down" icon={CreditCard} index={1} />
        <StatCard label="Refunded" value={formatCurrency(refunded)} change="+1.4%" icon={RefreshCcw} index={2} />
      </div>

      <PaymentsTable payments={payments} />
    </div>
  );
}
