from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
)
from fastapi.staticfiles import StaticFiles

from app.dependencies.database import create_db_and_tables
from app.routers import general_routes, rooms_routes

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

app.include_router(general_routes.router)
app.include_router(rooms_routes.router)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
