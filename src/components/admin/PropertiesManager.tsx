"use client";

import { useMemo, useState } from "react";
import {
  Briefcase,
  Building2,
  CheckCircle2,
  Copy,
  GraduationCap,
  Home,
  MapPin,
  Palmtree,
  Pencil,
  Plus,
  Search,
  SlidersHorizontal,
  Trash2,
  Users,
} from "lucide-react";
import { Listing, PropertyType } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { StarRating } from "@/components/ui/StarRating";
import { Switch } from "@/components/ui/Switch";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { StatCard } from "@/components/admin/StatCard";
import { formatCurrency } from "@/lib/utils";
import { unsplash } from "@/lib/images";

const typeMeta: Record<PropertyType, { label: string; icon: typeof Building2; image: Parameters<typeof unsplash>[0] }> = {
  hotel: { label: "Hotel Room", icon: Building2, image: "hotelSuite" },
  villa: { label: "Villa", icon: Palmtree, image: "villaPool" },
  house: { label: "House", icon: Home, image: "houseModern" },
  coworking: { label: "Work Room", icon: Briefcase, image: "coworkingDesk" },
  hostel: { label: "College Room", icon: GraduationCap, image: "hostelDorm" },
};

const typeTabs: Array<PropertyType | "all"> = ["all", "hotel", "villa", "house", "coworking", "hostel"];

const priceUnit: Record<PropertyType, string> = {
  hotel: "/night",
  villa: "/night",
  house: "/night",
  coworking: "/day",
  hostel: "/night",
};

const emptyForm = {
  name: "",
  propertyType: "hotel" as PropertyType,
  roomType: "",
  city: "",
  price: "",
  guests: "2",
  bedrooms: "1",
  bathrooms: "1",
  size: "300",
  description: "",
  amenities: "",
  tags: "",
};

export function PropertiesManager({ initialListings }: { initialListings: Listing[] }) {
  const [items, setItems] = useState(initialListings);
  const [query, setQuery] = useState("");
  const [type, setType] = useState<PropertyType | "all">("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [toast, setToast] = useState("");
  const [form, setForm] = useState(emptyForm);

  const filtered = useMemo(() => {
    return items.filter((l) => {
      const matchesType = type === "all" || l.propertyType === type;
      const q = query.trim().toLowerCase();
      const matchesQuery = !q || l.name.toLowerCase().includes(q) || l.city.toLowerCase().includes(q);
      return matchesType && matchesQuery;
    });
  }, [items, query, type]);

  const stats = useMemo(() => {
    const active = items.filter((l) => l.available).length;
    const avgPrice = items.length ? Math.round(items.reduce((s, l) => s + l.pricePerNight, 0) / items.length) : 0;
    return { total: items.length, active, inactive: items.length - active, avgPrice };
  }, [items]);

  function showToast(message: string) {
    setToast(message);
    setTimeout(() => setToast(""), 2200);
  }

  function toggleAvailability(id: string) {
    setItems((prev) => prev.map((l) => (l.id === id ? { ...l, available: !l.available } : l)));
  }

  function removeListing(id: string) {
    setItems((prev) => prev.filter((l) => l.id !== id));
    showToast("Property removed");
  }

  function duplicateListing(listing: Listing) {
    const copy: Listing = {
      ...listing,
      id: `L-${Math.floor(1000 + Math.random() * 9000)}`,
      slug: `${listing.slug}-copy-${Math.floor(Math.random() * 1000)}`,
      name: `${listing.name} (Copy)`,
      reviewCount: 0,
      rating: listing.rating,
      featured: false,
    };
    setItems((prev) => [copy, ...prev]);
    showToast("Property duplicated");
  }

  function openAddModal() {
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  function openEditModal(listing: Listing) {
    setEditingId(listing.id);
    setForm({
      name: listing.name,
      propertyType: listing.propertyType,
      roomType: listing.roomType,
      city: listing.city,
      price: String(listing.pricePerNight),
      guests: String(listing.guests),
      bedrooms: String(listing.bedrooms),
      bathrooms: String(listing.bathrooms),
      size: String(listing.size),
      description: listing.description,
      amenities: listing.amenities.join(", "),
      tags: listing.tags.join(", "),
    });
    setModalOpen(true);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim() || !form.city.trim() || !form.price) return;

    const amenities = form.amenities
      .split(",")
      .map((a) => a.trim())
      .filter(Boolean);
    const tags = form.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    if (editingId) {
      setItems((prev) =>
        prev.map((l) =>
          l.id === editingId
            ? {
                ...l,
                name: form.name.trim(),
                propertyType: form.propertyType,
                roomType: form.roomType.trim() || typeMeta[form.propertyType].label,
                city: form.city.trim(),
                location: form.city.trim() !== l.city ? form.city.trim() : l.location,
                pricePerNight: Number(form.price),
                guests: Number(form.guests),
                bedrooms: Number(form.bedrooms),
                bathrooms: Number(form.bathrooms),
                size: Number(form.size),
                description: form.description.trim() || l.description,
                amenities: amenities.length ? amenities : l.amenities,
                tags: tags.length ? tags : l.tags,
              }
            : l
        )
      );
      showToast("Property updated successfully");
    } else {
      const newListing: Listing = {
        id: `L-${Math.floor(1000 + Math.random() * 9000)}`,
        slug: form.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        name: form.name.trim(),
        propertyType: form.propertyType,
        roomType: form.roomType.trim() || typeMeta[form.propertyType].label,
        city: form.city.trim(),
        location: form.city.trim(),
        pricePerNight: Number(form.price),
        rating: 4.5,
        reviewCount: 0,
        guests: Number(form.guests),
        bedrooms: Number(form.bedrooms),
        bathrooms: Number(form.bathrooms),
        size: Number(form.size),
        images: [unsplash(typeMeta[form.propertyType].image)],
        amenities: amenities.length ? amenities : ["Free WiFi"],
        description: form.description.trim() || "Newly added property — details coming soon.",
        tags: tags.length ? tags : ["New"],
        available: true,
      };
      setItems((prev) => [newListing, ...prev]);
      showToast("Property added successfully");
    }

    setModalOpen(false);
    setEditingId(null);
    setForm(emptyForm);
  }

  return (
    <div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Properties" value={String(stats.total)} change="Live" icon={SlidersHorizontal} index={0} />
        <StatCard label="Active Listings" value={String(stats.active)} change={`${stats.total ? Math.round((stats.active / stats.total) * 100) : 0}%`} icon={CheckCircle2} index={1} />
        <StatCard label="Inactive" value={String(stats.inactive)} change="Paused" trend="down" icon={SlidersHorizontal} index={2} />
        <StatCard label="Avg. Price" value={formatCurrency(stats.avgPrice)} change="Blended" icon={Building2} index={3} />
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search properties by name or city"
            className="w-full rounded-full bg-slate-50 py-2.5 pl-10 pr-4 text-sm outline-none ring-1 ring-slate-100 transition-all focus:ring-primary-300"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {typeTabs.map((t) => {
            const Icon = t === "all" ? SlidersHorizontal : typeMeta[t].icon;
            return (
              <button
                key={t}
                onClick={() => setType(t)}
                className={`flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-semibold transition-all duration-200 ${
                  type === t
                    ? "bg-primary-700 text-white shadow-md shadow-primary-900/25"
                    : "bg-slate-50 text-slate-500 hover:bg-primary-50 hover:text-primary-700"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {t === "all" ? "All Types" : typeMeta[t].label}
              </button>
            );
          })}
        </div>
        <Button variant="accent" size="sm" onClick={openAddModal}>
          <Plus className="h-4 w-4" /> Add Property
        </Button>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((listing, i) => (
          <div
            key={listing.id}
            className="animate-fade-up overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100 transition-shadow duration-300 hover:shadow-lg"
            style={{ animationDelay: `${Math.min(i, 8) * 0.05}s` }}
          >
            <div className="relative h-40 w-full">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={listing.images[0]} alt={listing.name} className="h-full w-full object-cover" />
              <Badge tone="primary" className="absolute left-3 top-3">
                {typeMeta[listing.propertyType].label}
              </Badge>
            </div>
            <div className="p-4">
              <h3 className="truncate font-heading text-sm font-bold text-primary-900">{listing.name}</h3>
              <p className="truncate text-xs text-slate-400">{listing.roomType}</p>
              <div className="mt-1.5 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> {listing.city}
                </span>
                <span className="flex items-center gap-1">
                  <Users className="h-3 w-3" /> {listing.guests}
                </span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <StarRating rating={listing.rating} size={12} />
                <span className="text-sm font-bold text-primary-800">
                  {formatCurrency(listing.pricePerNight)}
                  <span className="text-xs font-medium text-slate-400">{priceUnit[listing.propertyType]}</span>
                </span>
              </div>

              <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3">
                <div className="flex items-center gap-2">
                  <Switch checked={listing.available} onChange={() => toggleAvailability(listing.id)} />
                  <span className="text-xs font-medium text-slate-500">
                    {listing.available ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => duplicateListing(listing)}
                    title="Duplicate"
                    className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-700"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => openEditModal(listing)}
                    title="Edit"
                    className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-700"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => removeListing(listing.id)}
                    title="Delete"
                    className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-accent-50 hover:text-accent-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="mt-10 text-center text-sm text-slate-400">No properties match your search.</p>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingId ? "Edit Property" : "Add New Property"}
      >
        <form onSubmit={handleSubmit} className="max-h-[70vh] space-y-3.5 overflow-y-auto pr-1">
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Property Name
            </label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Coral Bay Villa"
              className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Category
              </label>
              <select
                value={form.propertyType}
                onChange={(e) => setForm((f) => ({ ...f, propertyType: e.target.value as PropertyType }))}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              >
                {(Object.keys(typeMeta) as PropertyType[]).map((key) => (
                  <option key={key} value={key}>
                    {typeMeta[key].label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Room / Unit Type
              </label>
              <input
                value={form.roomType}
                onChange={(e) => setForm((f) => ({ ...f, roomType: e.target.value }))}
                placeholder={typeMeta[form.propertyType].label}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                City
              </label>
              <input
                value={form.city}
                onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
                placeholder="e.g. Goa"
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Price {priceUnit[form.propertyType]} (₹)
              </label>
              <input
                type="number"
                min={0}
                value={form.price}
                onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
                placeholder="5000"
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-4 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Guests
              </label>
              <input
                type="number"
                min={1}
                value={form.guests}
                onChange={(e) => setForm((f) => ({ ...f, guests: e.target.value }))}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Beds
              </label>
              <input
                type="number"
                min={0}
                value={form.bedrooms}
                onChange={(e) => setForm((f) => ({ ...f, bedrooms: e.target.value }))}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Baths
              </label>
              <input
                type="number"
                min={0}
                value={form.bathrooms}
                onChange={(e) => setForm((f) => ({ ...f, bathrooms: e.target.value }))}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Size (sqft)
              </label>
              <input
                type="number"
                min={0}
                value={form.size}
                onChange={(e) => setForm((f) => ({ ...f, size: e.target.value }))}
                className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Description
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={3}
              placeholder="Short description guests will see..."
              className="w-full resize-none rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Amenities (comma separated)
            </label>
            <input
              value={form.amenities}
              onChange={(e) => setForm((f) => ({ ...f, amenities: e.target.value }))}
              placeholder="Free WiFi, Air Conditioning, Parking"
              className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Tags (comma separated)
            </label>
            <input
              value={form.tags}
              onChange={(e) => setForm((f) => ({ ...f, tags: e.target.value }))}
              placeholder="Best Seller, Free Cancellation"
              className="w-full rounded-xl bg-slate-50 px-4 py-2.5 text-sm outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-primary-400"
            />
          </div>

          <Button type="submit" variant="primary" fullWidth className="mt-2">
            {editingId ? (
              <>
                <Pencil className="h-4 w-4" /> Save Changes
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" /> Add Property
              </>
            )}
          </Button>
        </form>
      </Modal>

      {toast && (
        <div className="animate-fade-up fixed bottom-6 right-6 z-[300] flex items-center gap-2 rounded-xl bg-primary-900 px-4 py-3 text-sm font-medium text-white shadow-2xl">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" /> {toast}
        </div>
      )}
    </div>
  );
}
