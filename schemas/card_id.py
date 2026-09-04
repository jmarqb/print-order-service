from pydantic import BaseModel

from schemas.address import Address


class CardId(BaseModel):
    number: str
    person_name: str
    address: Address
    volume: int
    folio: int
