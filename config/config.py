from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from pydantic_settings import BaseSettings

import models as models


class Settings(BaseSettings):
    MONGO_HOST: Optional[str]
    TEST_MONGO_HOST: Optional[str]

    APP_JWT_SECRET: str = "secret"
    ALGORITHM: str = "HS256"

    APP_PORT: Optional[int] = 8080

    DEBUG: bool = True

    MS_ROOT_PATH: str = "/ms-print/api"

    class Config:
        env_file = ".env"
        from_attributes = True


async def initiate_database(stage: str = None):
    settings = Settings()
    db_url = settings.TEST_MONGO_HOST if stage == "test" else settings.MONGO_HOST

    # await init_beanie(
    #     connection_string=db_url,
    #     document_models=models.__all__,
    # )
    client = AsyncIOMotorClient(host=db_url)

    await init_beanie(connection_string=db_url, document_models=models.__all__)

    return client
