from pydantic import BaseModel


class RequestSummaryResponse(BaseModel):
    client_app: str | None = ''
    total_requests: int | None = 0
    unprocess: int | None = 0
    processed: int | None = 0
    total_passport_requests: int | None = 0
    passport_requests_proccessed: int | None = 0
    passport_requests_unproccess: int | None = 0
    total_dni_requests: int | None = 0
    dni_requests_proccessed: int | None = 0
    dni_requests_unproccess: int | None = 0
    total_accreditation_requests: int | None = 0
    accreditation_requests_proccessed: int | None = 0
    accreditation_requests_unproccess: int | None = 0
