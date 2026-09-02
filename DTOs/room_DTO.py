from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator


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
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("Funny search terms are not allowed 🤨")
        return search
