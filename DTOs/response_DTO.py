from pydantic import BaseModel


class RoomResponse(BaseModel):
    id: int
    name: str
    price_per_night: int
    bedrooms: float
    bathrooms: float
    location: str
    amenities: str | None = None
    availability: bool

    class Config:
        from_attributes = True
