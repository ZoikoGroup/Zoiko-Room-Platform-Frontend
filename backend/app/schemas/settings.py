from app.schemas.common import CamelModel


class BrandingRead(CamelModel):
    logo_url: str


class BrandingUpdate(CamelModel):
    logo_url: str


class ProfileUpdate(CamelModel):
    full_name: str
    email: str
    phone: str = ""


class NotificationsRead(CamelModel):
    new_booking: bool
    payments: bool
    reviews: bool
    marketing: bool


class NotificationsUpdate(CamelModel):
    new_booking: bool
    payments: bool
    reviews: bool
    marketing: bool
