from beanie import PydanticObjectId
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from models.order import Order
from schemas import PaginatedResponse
from schemas.document_type import DocumentType
from services.order import order_service
from routes.auth import get_current_client


class CreateOrder(BaseModel):
    document_type: DocumentType


router = APIRouter(prefix="/v1/orders")


@router.get("/", response_model=PaginatedResponse, status_code=status.HTTP_200_OK)
async def get_order(
        page: int = Query(1, min=1),
        limit: int = Query(10, min=2),
        current_client: dict = Depends(get_current_client),
):
    owner = current_client["id"]

    return await order_service.get_orders(page, limit, owner)


@router.get("/{id}", response_model=Order, status_code=status.HTTP_200_OK)
async def get_order(
        id: PydanticObjectId, current_client: dict = Depends(get_current_client)
):
    owner = current_client["id"]
    return await order_service.get_order(str(id), owner)


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
        body: CreateOrder, current_client: dict = Depends(get_current_client)
):
    owner = current_client["id"]
    return await order_service.create_order(body.document_type, owner)
