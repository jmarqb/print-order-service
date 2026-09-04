from typing import Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.config import Settings
from schemas import Token
from services.auth import auth_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{Settings().MS_ROOT_PATH}/v1/auth/login"
)

router = APIRouter(prefix="/v1/auth")


async def get_current_client(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    return auth_service.validate_token(token)


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    client = await auth_service.authenticate_client(
        form_data.username, form_data.password
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(client)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/client/me/")
async def read_client_me(
        current_client: Annotated[Any, Depends(get_current_client)],
) -> Any:
    return current_client
