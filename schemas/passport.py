from pydantic import BaseModel


class Passport(BaseModel):
    number: str
    person_name: str
    city_birth: str
    country_birth: str
