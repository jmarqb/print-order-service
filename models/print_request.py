from typing import Optional, Any
from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel

from schemas import Passport, CardId, Accreditation, DocumentType


class PrintRequest(Document):
    id: Optional[PydanticObjectId] = ""
    reception_date: Optional[datetime]
    code: str
    document_type: DocumentType
    metadata: Passport | CardId | Accreditation
    processed: Optional[bool] = False
    associated_order: Optional[PydanticObjectId] | None = None
    owner: Optional[PydanticObjectId] | None = None
    cancelled: Optional[bool] = False

    class Settings:
        name = "printrequests"


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
