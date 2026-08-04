import Link from "next/link";
import { BedDouble, CalendarRange, IndianRupee, Users } from "lucide-react";
import { StatCard } from "@/components/admin/StatCard";
import { RevenueChart } from "@/components/admin/charts/RevenueChart";
import { BookingsByTypeChart } from "@/components/admin/charts/BookingsByTypeChart";
import { OccupancyChart } from "@/components/admin/charts/OccupancyChart";
import { Badge } from "@/components/ui/Badge";
import { StarRating } from "@/components/ui/StarRating";
import { bookings } from "@/data/bookings";
import { guests } from "@/data/guests";
import { listings } from "@/data/listings";
import { formatCurrency, formatDate } from "@/lib/utils";
import { bookingStatusTone } from "@/lib/status";

export default function AdminDashboardPage() {
  const totalRevenue = bookings.filter((b) => b.paymentStatus === "paid").reduce((s, b) => s + b.totalAmount, 0);
  const activeGuests = guests.filter((g) => g.status === "active").length;
  const avgRating = (listings.reduce((s, l) => s + l.rating, 0) / listings.length).toFixed(1);
  const recentBookings = [...bookings]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5);
  const topListings = [...listings].sort((a, b) => b.rating - a.rating).slice(0, 4);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-extrabold text-primary-900">Welcome back 👋</h1>
        <p className="mt-1 text-sm text-slate-500">Here&apos;s what&apos;s happening across your properties today.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Revenue" value={formatCurrency(totalRevenue)} change="+12.4%" icon={IndianRupee} index={0} />
        <StatCard label="Total Bookings" value={String(bookings.length)} change="+8.1%" icon={CalendarRange} index={1} />
        <StatCard label="Active Guests" value={String(activeGuests)} change="+4.6%" icon={Users} index={2} />
        <StatCard label="Avg. Rating" value={`${avgRating} / 5`} change="+0.2" icon={BedDouble} index={3} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="animate-fade-up rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-base font-bold text-primary-900">Revenue Trend</h2>
            <Badge tone="success">Last 6 months</Badge>
          </div>
          <div className="mt-2">
            <RevenueChart />
          </div>
        </div>

        <div className="animate-fade-up rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
          <h2 className="font-heading text-base font-bold text-primary-900">Bookings by Stay Type</h2>
          <div className="mt-4">
            <BookingsByTypeChart />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="animate-fade-up rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100 lg:col-span-2">
          <h2 className="font-heading text-base font-bold text-primary-900">Occupancy by City</h2>
          <div className="mt-2">
            <OccupancyChart />
          </div>
        </div>

        <div className="animate-fade-up rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-base font-bold text-primary-900">Top Listings</h2>
          </div>
          <div className="mt-3 space-y-3">
            {topListings.map((l) => (
              <div key={l.id} className="flex items-center gap-3 rounded-xl p-2 transition-colors hover:bg-primary-50">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={l.images[0]} alt={l.name} className="h-11 w-11 rounded-lg object-cover" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-primary-900">{l.name}</p>
                  <StarRating rating={l.rating} size={11} />
                </div>
                <span className="text-xs font-bold text-primary-700">{formatCurrency(l.pricePerNight)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="animate-fade-up rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
        <div className="flex items-center justify-between">
          <h2 className="font-heading text-base font-bold text-primary-900">Recent Bookings</h2>
          <Link href="/bookings" className="text-sm font-semibold text-primary-700 hover:text-accent-600">
            View all
          </Link>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-xs font-semibold uppercase tracking-wide text-slate-400">
                <th className="py-2.5 pr-4">Guest</th>
                <th className="py-2.5 pr-4">Property</th>
                <th className="py-2.5 pr-4">Dates</th>
                <th className="py-2.5 pr-4">Amount</th>
                <th className="py-2.5 pr-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentBookings.map((b) => (
                <tr key={b.id} className="border-b border-slate-50 transition-colors hover:bg-primary-50/50">
                  <td className="flex items-center gap-2.5 py-3 pr-4">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={b.guestAvatar} alt={b.guestName} className="h-8 w-8 rounded-full bg-primary-50" />
                    <span className="font-medium text-slate-700">{b.guestName}</span>
                  </td>
                  <td className="py-3 pr-4 text-slate-600">{b.listingName}</td>
                  <td className="py-3 pr-4 text-slate-500">
                    {formatDate(b.checkIn)} - {formatDate(b.checkOut)}
                  </td>
                  <td className="py-3 pr-4 font-semibold text-primary-900">{formatCurrency(b.totalAmount)}</td>
                  <td className="py-3 pr-4">
                    <Badge tone={bookingStatusTone[b.status]} className="capitalize">
                      {b.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
