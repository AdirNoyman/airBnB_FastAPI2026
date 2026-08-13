from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="Rent a room API",
    description="This is a simple API for renting rooms. You can create, read, update, and delete rooms using this API.",
    version="1.0.0",
    contact={"name": "Koko Loko", "email": "koko@gnail.com"},
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

mansions = [
    {
        "id": 1,
        "name": "Luxury mansion with pool",
        "price_per_night": 500,
        "location": "Los Angeles",
        "amenities": ["WiFi", "Pool", "Gym", "Parking"],
        "availability": True,
    },
    {
        "id": 2,
        "name": "Spacious mansion with garden",
        "price_per_night": 400,
        "location": "Miami",
        "amenities": ["WiFi", "Garden", "Parking"],
        "availability": False,
    },
    {
        "id": 3,
        "name": "Modern mansion with rooftop terrace",
        "price_per_night": 600,
        "location": "New York",
        "amenities": ["WiFi", "Rooftop Terrace", "Gym"],
        "availability": True,
    },
]

apartments = [
    {
        "id": 1,
        "name": "Sunny 2-bedroom apartment",
        "price_per_night": 100,
        "location": "New York",
        "amenities": ["WiFi", "Air Conditioning", "Kitchen"],
        "availability": True,
    },
    {
        "id": 2,
        "name": "Cozy 3-bedroom house",
        "price_per_night": 150,
        "location": "Los Angeles",
        "amenities": ["WiFi", "Pool", "Parking"],
        "availability": False,
    },
    {
        "id": 3,
        "name": "Modern studio near downtown",
        "price_per_night": 250,
        "location": "Chicago",
        "amenities": ["WiFi", "Gym", "Pet Friendly"],
        "availability": True,
    },
]


class Room(BaseModel):
    max_price: int | None = Field(default=None, ge=10, le=1000)
    search: str | None = Field(
        default=None,
        title="Search term",
        description="Search term for room names",
        min_length=3,
        max_length=10,
    )

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("Funny search terms are not allowed 🤨")
        return search


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to Rent a room API 🤓"}


# Annotated[Room, Query()] - This is a way to specify that the params argument should be of type Room and should be extracted from the query parameters of the request. The Query() function is used to indicate that the parameters should be taken from the query string of the URL.
@app.get("/mansions", status_code=status.HTTP_200_OK)
def get_mansions(params: Annotated[Room, Query()]):
    filtered_mansions = mansions
    if params.search:
        filtered_mansions = [
            room
            for room in filtered_mansions
            if params.search.lower() in room["name"].lower()
        ]
    if params.max_price:
        filtered_mansions = [
            room
            for room in filtered_mansions
            if room["price_per_night"] <= params.max_price
        ]
    return {"rooms": filtered_mansions}


@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms(params: Annotated[Room, Query()]):
    filtered_rooms = apartments
    if params.search:
        filtered_rooms = [
            room
            for room in filtered_rooms
            if params.search.lower() in room["name"].lower()
        ]
    if params.max_price:
        filtered_rooms = [
            room
            for room in filtered_rooms
            if room["price_per_night"] <= params.max_price
        ]
    return {"rooms": filtered_rooms}


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK)
def get_room(room_id: int):
    for room in apartments:
        if room["id"] == room_id:
            return {"room": room}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
