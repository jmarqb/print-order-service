from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from models.summary import RequestSummaryResponse
from routes.auth import get_current_client
from services.print_request import print_request_service

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
