"""Seeds the room-share marketplace domain: a super admin, a default active market
release, properties/rooms with verified authority + approved occupancy classification,
and published 30+ night listings -- plus guests/bookings/reviews so the dashboard has
real end-to-end data to show.

Run with: python seed.py
"""
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

from app.core.config import settings
from app.core.security import hash_password
from app.crud import finance as finance_crud
from app.crud import leasing as leasing_crud
from app.crud import occupancy as occupancy_crud
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (
    AdminSettings,
    AdminUser,
    Application,
    AuthorityRecord,
    Booking,
    Guest,
    Listing,
    MarketRelease,
    Membership,
    OccupancyClassification,
    Party,
    Payment,
    Property,
    Review,
    Room,
)
from app.schemas.finance import PaymentAllocationInput, PaymentConfirm, SimulatedPaymentCreate
from app.schemas.leasing import ApplicationCreate, ApplicationDecide, OfferTermsCreate

GUESTS = [
    dict(id="G-001", name="Aarav Mehta", email="aarav.mehta@example.com", phone="+91 98200 11223", location="Mumbai, IN", joined_at=date(2024, 2, 14), status="active"),
    dict(id="G-002", name="Isha Kapoor", email="isha.kapoor@example.com", phone="+91 98110 22334", location="Delhi, IN", joined_at=date(2024, 5, 2), status="active"),
    dict(id="G-003", name="Rohan Verma", email="rohan.verma@example.com", phone="+91 90040 33445", location="Bengaluru, IN", joined_at=date(2024, 8, 19), status="active"),
    dict(id="G-004", name="Sneha Iyer", email="sneha.iyer@example.com", phone="+91 99870 44556", location="Chennai, IN", joined_at=date(2023, 11, 30), status="active"),
    dict(id="G-005", name="Vikram Singh", email="vikram.singh@example.com", phone="+91 96500 55667", location="Jaipur, IN", joined_at=date(2025, 1, 11), status="inactive"),
]

# Each listing carries its own Property + Room, all private_room type with min_stay_nights=30.
LISTINGS = [
    dict(
        id="L-1001", slug="koramangala-private-room", name="Sunny Private Room in Koramangala Apartment",
        city="Bengaluru", address="4th Block, Koramangala, Bengaluru", location="Koramangala, Bengaluru",
        price_per_night=650, guests=1, bedrooms=1, bathrooms=1, size=140, has_ensuite=False,
        images=["hotelBedroom"], amenities=["Free WiFi", "Shared Kitchen", "Housekeeping", "Furnished"],
        description="A sunlit private room in a well-maintained 3BHK apartment, shared with two working professionals. Ideal for a 1+ month stay.",
        tags=["Long Stay", "Furnished"], featured=True,
    ),
    dict(
        id="L-1002", slug="andheri-west-room", name="Cozy Room in Andheri West Flat",
        city="Mumbai", address="Andheri West, Mumbai", location="Andheri West, Mumbai",
        price_per_night=720, guests=1, bedrooms=1, bathrooms=1, size=120, has_ensuite=True,
        images=["hotelRoom"], amenities=["Free WiFi", "Attached Bathroom", "Housekeeping", "Air Conditioning"],
        description="Private room with an attached bathroom in a quiet residential society, five minutes from the metro.",
        tags=["Ensuite", "Long Stay"], featured=False,
    ),
    dict(
        id="L-1003", slug="whitefield-quiet-room", name="Quiet Private Room near Whitefield Tech Park",
        city="Bengaluru", address="Whitefield, Bengaluru", location="Whitefield, Bengaluru",
        price_per_night=600, guests=1, bedrooms=1, bathrooms=1, size=130, has_ensuite=False,
        images=["hotelRoom2"], amenities=["Free WiFi", "Shared Kitchen", "Parking", "Furnished"],
        description="A quiet room in a gated community close to the tech park, shared with a small, respectful household.",
        tags=["Tech Commute", "Furnished"], featured=False,
    ),
    dict(
        id="L-1004", slug="kothrud-spacious-room", name="Spacious Room in Kothrud Apartment",
        city="Pune", address="Kothrud, Pune", location="Kothrud, Pune",
        price_per_night=550, guests=1, bedrooms=1, bathrooms=1, size=150, has_ensuite=False,
        images=["houseModern"], amenities=["Free WiFi", "Shared Kitchen", "Balcony", "Furnished"],
        description="A spacious, well-lit room with balcony access in a family-friendly apartment complex.",
        tags=["Long Stay", "Balcony"], featured=False,
    ),
]

BOOKINGS = [
    dict(id="BK-30001", listing_id="L-1001", guest_email="aarav.mehta@example.com", check_in=date(2026, 8, 10), check_out=date(2026, 9, 9), guests=1, status="confirmed", payment_status="paid", created_at=date(2026, 7, 20)),
    dict(id="BK-30002", listing_id="L-1002", guest_email="sneha.iyer@example.com", check_in=date(2026, 8, 1), check_out=date(2026, 10, 30), guests=1, status="confirmed", payment_status="paid", created_at=date(2026, 7, 10)),
    dict(id="BK-30003", listing_id="L-1003", guest_email="rohan.verma@example.com", check_in=date(2026, 9, 1), check_out=date(2026, 10, 1), guests=1, status="pending", payment_status="unpaid", created_at=date(2026, 8, 1)),
    dict(id="BK-30004", listing_id="L-1001", guest_email="isha.kapoor@example.com", check_in=date(2026, 5, 1), check_out=date(2026, 6, 1), guests=1, status="completed", payment_status="paid", created_at=date(2026, 4, 10)),
]

REVIEWS = [
    dict(id="RV-601", listing_id="L-1001", guest_email="isha.kapoor@example.com", rating=5, comment="Great flatmates, very clean, and the room stayed exactly as described for the whole month.", date=date(2026, 6, 3)),
    dict(id="RV-602", listing_id="L-1002", guest_email="sneha.iyer@example.com", rating=4, comment="Good location near the metro, ensuite bathroom was a big plus for a long stay.", date=date(2026, 8, 20)),
]

PAYMENT_METHODS = ["Credit Card", "UPI", "Net Banking", "PayPal", "Wallet"]

UNSPLASH_IDS = {
    "hotelBed": "1566073771259-6a8506099945",
    "hotelBedroom": "1582719478250-c89cae4dc85b",
    "hotelRoom": "1611892440504-42a792e24d32",
    "hotelRoom2": "1560185127-6ed189bf02f4",
    "houseModern": "1568605114967-8130f3a36994",
}


def unsplash_url(key: str, w: int = 1200, q: int = 80) -> str:
    return f"https://images.unsplash.com/photo-{UNSPLASH_IDS[key]}?w={w}&q={q}&auto=format&fit=crop"


def dicebear_avatar(name: str) -> str:
    return f"https://api.dicebear.com/9.x/notionists/svg?seed={quote(name)}&backgroundColor=eef2fa,fdecec"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.email == settings.seed_admin_email).first()
        if not admin:
            admin = AdminUser(
                email=settings.seed_admin_email,
                hashed_password=hash_password(settings.seed_admin_password),
                full_name="Zoiko Admin",
                role="super_admin",
            )
            admin.settings = AdminSettings()
            db.add(admin)
            db.flush()
        elif admin.role != "super_admin":
            admin.role = "super_admin"
            db.flush()

        # Default party/membership for the seed admin, standing in for the provider org
        # until self-service provider onboarding exists.
        membership = db.query(Membership).filter(Membership.admin_user_id == admin.id).first()
        if membership:
            party = membership.party
        else:
            party = Party(party_type="zoiko_operator")
            db.add(party)
            db.flush()
            db.add(Membership(admin_user_id=admin.id, party_id=party.id, role="provider_owner_admin"))
            db.flush()

        market_release = db.query(MarketRelease).filter(MarketRelease.jurisdiction == "IN").first()
        if not market_release:
            market_release = MarketRelease(
                jurisdiction="IN",
                status="active",
                min_stay_nights=30,
                effective_from=datetime.now(timezone.utc),
                approved_by_admin_id=admin.id,
                approved_at=datetime.now(timezone.utc),
            )
            db.add(market_release)
            db.flush()

        for row in LISTINGS:
            prop = db.query(Property).filter(Property.address == row["address"]).first()
            if not prop:
                prop = Property(owner_party_id=party.id, address=row["address"], city=row["city"])
                db.add(prop)
                db.flush()

            room = db.query(Room).filter(Room.property_id == prop.id).first()
            if not room:
                room = Room(property_id=prop.id, room_type="private_room", size=row["size"], has_ensuite=row["has_ensuite"])
                db.add(room)
                db.flush()

            authority = db.query(AuthorityRecord).filter(AuthorityRecord.room_id == room.id).first()
            if not authority:
                now = datetime.now(timezone.utc)
                db.add(
                    AuthorityRecord(
                        party_id=party.id,
                        room_id=room.id,
                        authority_type="ownership_declaration",
                        evidence_ref="seed-demo-evidence",
                        status="verified",
                        verified_at=now,
                        expires_at=now + timedelta(days=365),
                        verifier_admin_id=admin.id,
                    )
                )

            classification = db.query(OccupancyClassification).filter(OccupancyClassification.room_id == room.id).first()
            if not classification:
                db.add(
                    OccupancyClassification(
                        room_id=room.id,
                        classification="shared_residential_room",
                        confidence=1.0,
                        evidence_ref="seed-demo-classification",
                        jurisdiction="IN",
                        rule_version=1,
                        review_state="APPROVED",
                    )
                )
            db.flush()

            listing = Listing(
                id=row["id"],
                slug=row["slug"],
                name=row["name"],
                property_type="private_room",
                room_type="Private Room",
                city=row["city"],
                location=row["location"],
                price_per_night=row["price_per_night"],
                rating=4.5,
                review_count=0,
                guests=row["guests"],
                bedrooms=row["bedrooms"],
                bathrooms=row["bathrooms"],
                size=row["size"],
                images=[unsplash_url(img) for img in row["images"]],
                amenities=row["amenities"],
                tags=row["tags"],
                description=row["description"],
                featured=row["featured"],
                owner_id=admin.id,
                room_id=room.id,
                market_release_id=market_release.id,
                min_stay_nights=30,
                state="PUBLISHED",
            )
            db.merge(listing)

        guests_by_email = {}
        for row in GUESTS:
            guest = Guest(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                phone=row["phone"],
                avatar=dicebear_avatar(row["name"]),
                location=row["location"],
                joined_at=row["joined_at"],
                status=row["status"],
            )
            db.merge(guest)
            guests_by_email[row["email"]] = row["id"]
        db.flush()

        for i, row in enumerate(BOOKINGS):
            booking = Booking(
                id=row["id"],
                listing_id=row["listing_id"],
                guest_id=guests_by_email[row["guest_email"]],
                check_in=row["check_in"],
                check_out=row["check_out"],
                guests=row["guests"],
                status=row["status"],
                payment_status=row["payment_status"],
                created_at=row["created_at"],
            )
            db.merge(booking)
            db.merge(
                Payment(
                    id=f"PAY-{8000 + i}",
                    booking_id=row["id"],
                    method=PAYMENT_METHODS[i % len(PAYMENT_METHODS)],
                    status=row["payment_status"],
                    date=row["created_at"],
                )
            )

        for row in REVIEWS:
            review = Review(
                id=row["id"],
                listing_id=row["listing_id"],
                guest_id=guests_by_email[row["guest_email"]],
                rating=row["rating"],
                comment=row["comment"],
                date=row["date"],
            )
            db.merge(review)

        db.commit()

        seed_leasing_pipeline(db, admin)

        print(f"Seed complete. Super admin login: {settings.seed_admin_email} / (password set in .env SEED_ADMIN_PASSWORD)")
    finally:
        db.close()


def seed_leasing_pipeline(db, admin: AdminUser) -> None:
    """Walks the real application->offer->agreement->payment->occupancy->payout->
    reconciliation pipeline through the actual CRUD layer (not hand-crafted rows),
    on top of the L-1001 listing seeded above -- so the dashboard has one fully
    worked example, and this doubles as an integration check of the whole flow."""
    application = db.query(Application).filter_by(listing_id="L-1001", guest_id="G-001").first()
    if application:
        return  # already seeded on a prior run

    application = leasing_crud.submit_application(
        db,
        ApplicationCreate(
            listing_id="L-1001",
            guest_id="G-001",
            message="Looking for a quiet long-term room close to work.",
            desired_move_in=date.today(),
        ),
    )
    leasing_crud.decide_application(db, application, admin, ApplicationDecide(decision="APPROVED", reason_code="good_fit"))

    offer = leasing_crud.create_offer(db, application, admin)
    leasing_crud.add_offer_terms(
        db,
        offer,
        admin,
        OfferTermsCreate(monthly_rent=18000, deposit_amount=36000, start_date=date.today(), term_months=11),
    )
    leasing_crud.set_offer_status(db, offer, admin, "SENT")
    leasing_crud.set_offer_status(db, offer, admin, "ACCEPTED")

    agreement = leasing_crud.create_agreement(db, offer, admin)
    leasing_crud.send_agreement(db, agreement, admin)
    leasing_crud.sign_agreement(db, agreement, "provider", admin)
    agreement = leasing_crud.sign_agreement(db, agreement, "renter", admin)

    rent_obligation = next(o for o in agreement.obligations if o.obligation_type == "RENT")
    deposit_obligation = next(o for o in agreement.obligations if o.obligation_type == "DEPOSIT")

    payment = finance_crud.create_payment_intent(
        db,
        SimulatedPaymentCreate(guest_id="G-001", amount=54000, currency="INR", idempotency_key="SEED-PAY-0001"),
    )
    finance_crud.confirm_payment(
        db,
        payment,
        PaymentConfirm(
            allocations=[
                PaymentAllocationInput(obligation_id=rent_obligation.id, amount=18000),
                PaymentAllocationInput(obligation_id=deposit_obligation.id, amount=36000),
            ]
        ),
        admin,
    )

    occupancy_crud.confirm_move_in(db, agreement, admin)

    party = db.get(Party, offer.listing.room.property.owner_party_id)
    finance_crud.run_payout(db, party, admin, period_key=date.today().strftime("%Y-%m"))
    finance_crud.run_reconciliation(db, admin)


if __name__ == "__main__":
    seed()
