import { Review } from "@/lib/types";
import { listings } from "./listings";
import { guests } from "./guests";

function listing(id: string) {
  return listings.find((l) => l.id === id)!;
}
function avatar(name: string) {
  return guests.find((g) => g.name === name)?.avatar ?? "";
}

const raw: Array<{ id: string; listingId: string; guestName: string; rating: number; comment: string; date: string }> = [
  { id: "RV-501", listingId: "L-1001", guestName: "Aarav Mehta", rating: 5, comment: "Stunning sea view and the bed was incredibly comfortable. Breakfast spread was excellent too.", date: "2026-07-14" },
  { id: "RV-502", listingId: "L-2001", guestName: "Sneha Iyer", rating: 5, comment: "The infinity pool alone is worth it. Staff arranged everything from groceries to a private chef.", date: "2026-05-08" },
  { id: "RV-503", listingId: "L-3002", guestName: "Priya Nair", rating: 4, comment: "Beautiful heritage property, loved the verandas. WiFi was a little patchy in the garden.", date: "2026-06-20" },
  { id: "RV-504", listingId: "L-1004", guestName: "Isha Kapoor", rating: 5, comment: "Butler service made our anniversary unforgettable. The lake view from the terrace is unreal.", date: "2026-08-08" },
  { id: "RV-505", listingId: "L-2002", guestName: "Karan Malhotra", rating: 4, comment: "Great for our group trip, bonfire nights were a highlight. Could use better hot water pressure.", date: "2026-07-02" },
  { id: "RV-506", listingId: "L-1002", guestName: "Ananya Rao", rating: 4, comment: "Perfect for a work trip — fast WiFi, quiet rooms, and close to BKC offices.", date: "2026-07-27" },
  { id: "RV-507", listingId: "L-3001", guestName: "Meera Pillai", rating: 5, comment: "Woke up to lake views every morning. The fireplace was perfect for the Nainital chill.", date: "2026-08-01" },
  { id: "RV-508", listingId: "L-2003", guestName: "Rohan Verma", rating: 5, comment: "Absolutely stunning beachfront villa, the games room kept the kids entertained all day.", date: "2026-04-22" },
  { id: "RV-509", listingId: "L-1003", guestName: "Vikram Singh", rating: 4, comment: "Good value stay near the bazaars, simple but clean rooms.", date: "2026-03-30" },
  { id: "RV-510", listingId: "L-1001", guestName: "Aditya Kulkarni", rating: 5, comment: "One of the best hotel stays in Goa. Would book again in a heartbeat.", date: "2026-07-21" },
];

export const reviews: Review[] = raw.map((r) => {
  const l = listing(r.listingId);
  return {
    id: r.id,
    listingId: r.listingId,
    listingName: l.name,
    guestName: r.guestName,
    guestAvatar: avatar(r.guestName),
    rating: r.rating,
    comment: r.comment,
    date: r.date,
    propertyType: l.propertyType,
  };
});
