from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from bson import ObjectId
from pwdlib import PasswordHash

from config.config import Settings
from database import database
from models.client_app import ClientApp

password_hash = PasswordHash.recommended()
settings = Settings()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def save_client(name: str, url: str, password: str):
    format_name = name.lower()
    exist_client = await database.exists_client_app(format_name)
    if exist_client is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Name {name} already exists",
        )
    format_url = url.lower()
    encrypt_password = password_hash.hash(password)
    client_app_data = {
        "id": ObjectId(),
        "name": format_name,
        "url": format_url,
        "password": encrypt_password,
    }
    return await database.insert_client_app(client_app_data)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


async def authenticate_client(username: str, password: str):
    client = await database.get_client_app(username)
    if not client:
        dummy_password = password_hash.hash(password)
        verify_password(password, dummy_password)
        return False

    if not verify_password(password, client.password):
        return False
    return client


def create_access_token(client: ClientApp):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    data = {"sub": client.name, "id": str(client.id), "issuer": "ms-print"}
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.APP_JWT_SECRET, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def validate_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.APP_JWT_SECRET, algorithms=settings.ALGORITHM
        )
        return payload
    except jwt.PyJWTError:
        raise credentials_exception
