from pydantic import BaseModel

from schemas.accreditation_period import AccreditationPeriod


class Accreditation(BaseModel):
    number: str
    person_name: str
    origin_country: str
    accreditation_period: AccreditationPeriod
    responsability: str
