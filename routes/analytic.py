from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from routes.auth import get_current_client
from services.print_request import print_request_service


class RequestSummaryResponse(BaseModel):
    client_app: str
    total_requests: int
    unprocess: int
    processed: int
    total_passport_requests: int
    passport_requests_proccessed: int
    passport_requests_unproccess: int
    total_dni_requests: int
    dni_requests_proccessed: int
    dni_requests_unproccess: int
    total_accreditation_requests: int
    accreditation_requests_proccessed: int
    accreditation_requests_unproccess: int


router = APIRouter(prefix="/v1/analytics")


@router.get(
    "/requests-summary",
    response_model=RequestSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_print_request_summary(
    current_client: dict = Depends(get_current_client),
) -> RequestSummaryResponse:
    owner = PydanticObjectId(current_client["id"])
    return await print_request_service.get_requests_analytics_summary(owner)
