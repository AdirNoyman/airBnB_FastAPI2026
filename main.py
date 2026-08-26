from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, func, or_, select

from database import SessionDependency, create_db_and_tables
from DTOs.create_DTO import RoomCreate
from DTOs.response_DTO import RoomResponse
from DTOs.update_DTO import RoomUpdate
from models.models import Room

openapi_tags = [
    {
        "name": "Rooms",
        "description": "Operations with rooms. The **login** logic is also here.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up 🚀...")
    create_db_and_tables()  # Create the database tables on startup
    yield
    # Code to run on shutdown
    print("Shutting down 😴...")


app = FastAPI(
    lifespan=lifespan,
    title="Rent a room API",
    description="This is a simple API for renting rooms. You can create, read, update, and delete rooms using this API.",
    version="1.0.0",
    contact={"name": "Koko Loko", "email": "koko@gnail.com"},
    openapi_tags=openapi_tags,
)


app.mount("/assets", StaticFiles(directory="assets"), name="assets")


class AppCookie(BaseModel):
    # Literal is like an enum.
    theme: Literal["light", "dark"] = "dark"
    language: Literal["en", "es", "fr"] = "en"


class RoomDTO(BaseModel):
    max_price: int | None = Field(
        default=None,
        ge=10,
        le=1000,
        examples=[100, 200, 300],
        description="Maximum price per night for the room",
    )
    search: Annotated[str | None, StringConstraints(to_lower=True)] = Field(
        default=None,
        title="Search term",
        description="Search term for room names",
        min_length=3,
        max_length=10,
        examples=["luxury", "cozy", "modern"],
    )

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("Funny search terms are not allowed 🤨")
        return search


@app.get("/", status_code=status.HTTP_200_OK)
# Cookie() - instruct FastAPI to look for the 'language' parameter in the cookie coming in the user request
# Header() - instruct FastAPI to look for the 'user_agent' parameter in the header coming in the user request
def root(
    app_cookie: Annotated[AppCookie, Cookie()], user_agent: Annotated[str, Header()]
):

    greetings = {
        "en": "Welcome to Rent a room API 🤓",
        "es": "¡Bienvenido a Rent a room API 🤓",
        "fr": "Bienvenue sur Rent a room API 🤓",
    }
    return {"message": greetings.get(app_cookie.language), "user_agent": user_agent}


# Annotated[Room, Query()] - This is a way to specify that the params argument should be of type Room and should be extracted from the query parameters of the request. The Query() function is used to indicate that the parameters should be taken from the query string of the URL.
@app.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
    tags=["Rooms"],
    summary="Get all rooms",
    description="Get all rooms with optional filtering by search term and maximum price",
    response_description="A list of rooms matching the search criteria",
)
# Query() - instruct FastAPI to look for the parameters in the query params
def get_rooms(session: SessionDependency, params: Annotated[RoomDTO, Query()]):

    query = select(Room)

    if params.max_price:
        query = query.where(Room.price_per_night <= params.max_price)

    if params.search:
        query = query.where(func.lower(Room.name).contains(params.search))

    filtered_rooms = session.exec(query).all()

    return {"rooms": filtered_rooms}


@app.get(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    tags=["Rooms"],
    summary="Get a specific room",
    description="Get a specific room by its ID",
    response_description="The room details",
)
def get_room(session: SessionDependency, room_id: int):
    room = session.get(Room, room_id)
    if room:
        return room
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )


@app.post(
    "/rooms",
    status_code=status.HTTP_201_CREATED,
    tags=["Rooms"],
    response_model=RoomResponse,
)
def create_new_room(session: SessionDependency, room: RoomCreate) -> Room:
    db_room = Room(**room.model_dump())
    session.add(db_room)
    session.commit()
    session.refresh(db_room)
    return db_room


# The server tells the client to store the cookies in the browser. The cookies will be sent back to the server with every subsequent request, allowing the server to remember the user's preferences.
@app.post(
    "/preferences", status_code=status.HTTP_201_CREATED, tags=["Client Preferences"]
)
def set_preferences(response: Response):
    app_cookie = AppCookie()
    response.set_cookie(key="theme", value=app_cookie.theme)
    response.set_cookie(key="language", value=app_cookie.language)
    return {"message": "User preferences set successfully"}
