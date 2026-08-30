from typing import Optional, Any
from beanie import Document, PydanticObjectId
from pydantic import BaseModel


class ClientApp(Document):
    id: Optional[PydanticObjectId] = ""
    name: str
    url: str
    password: str
    active: Optional[bool] = True

    class Settings:
        name = "clientapps"


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation successful",
                "data": "Sample data",
            }
        }
