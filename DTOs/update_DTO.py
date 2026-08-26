from pydantic import BaseModel, Field


class RoomUpdate(BaseModel):
    name: str | None = None
    price_per_night: int | None = None
    bedrooms: float | None = Field(default=None, multiple_of=0.5, ge=0)
    bathrooms: float | None = Field(default=None, multiple_of=0.5, ge=0)
    location: str | None = None
    amenities: str | None = None
    availability: bool | None = None
