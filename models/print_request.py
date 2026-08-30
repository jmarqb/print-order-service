from typing import Optional, Any
from enum import Enum
from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel


class DocumentType(str, Enum):
    PASSPORT = "PASSPORT"
    DNI = "DNI"
    ACCREDITATION = "ACCREDITATION"


class Address(BaseModel):
    main_street: str
    between_streets: str
    number: int
    municipality: str
    state: str


class AccreditationPeriod(BaseModel):
    start_date: datetime
    end_date: datetime


class Passport(BaseModel):
    number: str
    person_name: str
    city_birth: str
    country_birth: str


class CardId(BaseModel):
    number: str
    person_name: str
    address: Address
    volume: int
    folio: int


class Accreditation(BaseModel):
    number: str
    person_name: str
    origin_country: str
    accreditation_period: AccreditationPeriod
    responsability: str


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
