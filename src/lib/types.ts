export type PropertyType = "hotel" | "villa" | "house" | "coworking" | "hostel";

export type BookingStatus = "confirmed" | "pending" | "cancelled" | "completed";
export type PaymentStatus = "paid" | "unpaid" | "refunded";

export interface Listing {
  id: string;
  slug: string;
  name: string;
  propertyType: PropertyType;
  roomType: string;
  city: string;
  location: string;
  pricePerNight: number;
  rating: number;
  reviewCount: number;
  guests: number;
  bedrooms: number;
  bathrooms: number;
  size: number;
  images: string[];
  amenities: string[];
  description: string;
  tags: string[];
  featured?: boolean;
  available: boolean;
}

export interface Booking {
  id: string;
  listingId: string;
  listingName: string;
  propertyType: PropertyType;
  guestName: string;
  guestEmail: string;
  guestAvatar: string;
  checkIn: string;
  checkOut: string;
  nights: number;
  guests: number;
  totalAmount: number;
  status: BookingStatus;
  paymentStatus: PaymentStatus;
  createdAt: string;
}

export interface Guest {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar: string;
  location: string;
  totalBookings: number;
  totalSpent: number;
  joinedAt: string;
  status: "active" | "inactive";
}

export interface Review {
  id: string;
  listingId: string;
  listingName: string;
  guestName: string;
  guestAvatar: string;
  rating: number;
  comment: string;
  date: string;
  propertyType: PropertyType;
}

export interface Payment {
  id: string;
  bookingId: string;
  guestName: string;
  amount: number;
  method: "Credit Card" | "UPI" | "Net Banking" | "PayPal" | "Wallet";
  status: PaymentStatus;
  date: string;
}
