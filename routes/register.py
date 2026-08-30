from fastapi import APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from models.client_app import ClientApp
from services.auth import auth_service

router = APIRouter(prefix="/v1/auth")


class RegisterClientApp(BaseModel):
    name: str = Field(min_length=2, title="Client app name")
    url: str = Field(title="Client app url")
    password: str | int = Field(title="Password")


@router.post("/signup", response_model=ClientApp, status_code=status.HTTP_201_CREATED)
async def register(register_client: RegisterClientApp):
    return await auth_service.save_client(
        register_client.name, register_client.url, str(register_client.password)
    )
