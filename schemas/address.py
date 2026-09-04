from pydantic import BaseModel


class Address(BaseModel):
    main_street: str
    between_streets: str
    number: int
    municipality: str
    state: str