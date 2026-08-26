from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    name: str
    price_per_night: int
    bedrooms: float = Field(multiple_of=0.5, ge=0)
    bathrooms: float = Field(multiple_of=0.5, ge=0)
    location: str
    amenities: str | None = None
    availability: bool
