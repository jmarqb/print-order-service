from typing import Optional, List, Any
from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

from schemas.document_type import DocumentType


class Order(Document):
    id: Optional[PydanticObjectId] = ""
    date: Optional[datetime]
    code: str
    associated_print_requests: List[PydanticObjectId]
    print_requests_type: DocumentType
    print_requests_quantity: int = Field(ge=1, le=50)
    owner: Optional[PydanticObjectId] = ""

    class Settings:
        name = "orders"


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        json_schema = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation successful",
                "data": "Sample data",
            }
        }
