from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Header, Response, status
from pydantic import BaseModel

router = APIRouter()


class AppCookie(BaseModel):
    # Literal is like an enum.
    theme: Literal["light", "dark"] = "dark"
    language: Literal["en", "es", "fr"] = "en"


class AppHeaders(BaseModel):
    user_agent: str | None


@router.get("/", status_code=status.HTTP_200_OK)
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


# The server tells the client to store the cookies in the browser. The cookies will be sent back to the server with every subsequent request, allowing the server to remember the user's preferences.
@router.post(
    "/preferences", status_code=status.HTTP_201_CREATED, tags=["Client Preferences"]
)
def set_preferences(response: Response):
    app_cookie = AppCookie()
    response.set_cookie(key="theme", value=app_cookie.theme)
    response.set_cookie(key="language", value=app_cookie.language)
    return {"message": "User preferences set successfully"}
