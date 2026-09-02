from sqlmodel import Field, SQLModel

""" "id": 1,
        "name": "Sunny 2-bedroom apartment",
        "price_per_night": 100,
        "location": "New York",
        "amenities": ["WiFi", "Air Conditioning", "Kitchen"],
        "availability": True"""


class Room(SQLModel, table=True):
    __tablename__: str = "rooms"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price_per_night: int
    bedrooms: float = Field(multiple_of=0.5, ge=0)
    bathrooms: float = Field(multiple_of=0.5, ge=0)
    location: str
    amenities: str | None = Field(default=None)
    availability: bool
