from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import col, func, select

from app.dependencies.database import SessionDependency
from app.models.room import Room
from DTOs.create_DTO import RoomCreate
from DTOs.response_DTO import RoomResponse
from DTOs.room_DTO import RoomDTO
from DTOs.update_DTO import RoomUpdate

router = APIRouter()

RoomId = Annotated[int, Path(ge=1, description="The Id of the room to fetch")]


async def get_room_or_404(
    session: SessionDependency,
    room_id: RoomId,
) -> Room:
    room = await session.get(Room, room_id)
    if room:
        return room
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )


RooDependency = Annotated[Room, Depends(get_room_or_404)]

IS_MAINTENANCE_MODE = False  # Set to True to simulate maintenance mode


def check_maintenance_mode():
    if IS_MAINTENANCE_MODE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The service is temporarily unavailable due to maintenance.",
        )


# Annotated[Room, Query()] - This is a way to specify that the params argument should be of type Room and should be extracted from the query parameters of the request. The Query() function is used to indicate that the parameters should be taken from the query string of the URL.
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all rooms",
    description="Get all rooms with optional filtering by search term and maximum price",
    response_description="A list of rooms matching the search criteria",
)
# Query() - instruct FastAPI to look for the parameters in the query params
async def get_rooms(session: SessionDependency, params: Annotated[RoomDTO, Query()]):

    query = select(Room)

    if params.max_price:
        query = query.where(Room.price_per_night <= params.max_price)

    if params.search:
        query = query.where(func.lower(Room.name).contains(params.search))

    query = query.limit(params.limit).offset(params.offset).order_by(col(Room.id))

    result = await session.execute(query)
    rooms = result.scalars().all()

    return {"rooms": rooms, "count": len(rooms)}


# GET a room
@router.get(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a specific room",
    description="Get a specific room by its ID",
    response_model=RoomResponse,
    response_description="The room details",
)
async def get_room(room: RooDependency) -> Room:
    return room


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RoomResponse,
    dependencies=[Depends(check_maintenance_mode)],
)
async def create_new_room(session: SessionDependency, room: RoomCreate) -> Room:
    db_room = Room(**room.model_dump())
    session.add(db_room)
    await session.commit()
    await session.refresh(db_room)
    return db_room


@router.patch(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    summary="Update room data",
    description="Full or partial update of room data",
    response_model=RoomResponse,
    response_description="The updated room details",
)
async def update_room(
    session: SessionDependency, room: RooDependency, update_data: RoomUpdate
) -> Room:
    room.sqlmodel_update(update_data.model_dump(exclude_unset=True))
    session.add(room)
    await session.commit()
    await session.refresh(room)
    return room


# DELETE a room
@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a room",
    description="Permanently delete a room",
    response_description="The room was deleted successfully",
)
async def delete_room(session: SessionDependency, room: RooDependency):
    await session.delete(room)
    await session.commit()
