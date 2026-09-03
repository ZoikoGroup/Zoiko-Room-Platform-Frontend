from app.schemas.common import CamelModel


class SearchResult(CamelModel):
    id: str
    type: str  # "listing" | "guest" | "booking" | "application" | "occupancy"
    title: str
    subtitle: str
    href: str
