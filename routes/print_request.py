from typing import Any, List, Annotated
from fastapi import APIRouter, Depends, status, Query, Path
from beanie import PydanticObjectId
from pydantic import BaseModel, model_validator

from routes.auth import get_current_client
from schemas.document_type import DocumentType
from services.print_request import print_request_service
from models.print_request import (
    Passport,
    CardId,
    Accreditation,
    PrintRequest,
)


class CreatePrintRequest(BaseModel):
    document_type: DocumentType
    metadata: Any

    @model_validator(mode="before")
    @classmethod
    def validate_metadata_by_type(cls, values: dict[str, Any]) -> dict[str, Any]:
        doc_type = values.get("document_type")
        raw_metadata = values.get("metadata", {})

        if doc_type == DocumentType.PASSPORT:
            values["metadata"] = Passport.model_validate(raw_metadata)
        elif doc_type == DocumentType.DNI:
            values["metadata"] = CardId.model_validate(raw_metadata)
        elif doc_type == DocumentType.ACCREDITATION:
            values["metadata"] = Accreditation.model_validate(raw_metadata)
        return values


class PaginatedResponse(BaseModel):
    items: List[PrintRequest]
    total: int
    current_page: int
    total_pages: int


router = APIRouter(prefix="/v1/requests")


@router.get("/", response_model=PaginatedResponse, status_code=status.HTTP_200_OK)
async def get_print_requests(
        page: int = Query(1, min=1),
        limit: int = Query(10, min=2),
        current_client: dict = Depends(get_current_client),
):
    owner = current_client["id"]

    return await print_request_service.get_print_requests(page, limit, owner)


@router.get("/{id}", response_model=PrintRequest, status_code=status.HTTP_200_OK)
async def get_print_request(
        id: PydanticObjectId, current_client: dict = Depends(get_current_client)
):
    owner = current_client["id"]

    return await print_request_service.get_print_request(str(id), owner)


@router.post("/", response_model=PrintRequest, status_code=status.HTTP_201_CREATED)
async def create_print_request(
        body: CreatePrintRequest, current_client: dict = Depends(get_current_client)
):
    owner = current_client["id"]
    return await print_request_service.create_print_request(
        body.document_type, body.metadata, owner
    )


@router.put(
    "/id/{print_request_id}/document-type/passport",
    response_model=PrintRequest,
    status_code=status.HTTP_200_OK,
)
async def update_request_type_passport(
        print_request_id: Annotated[PydanticObjectId, Path(title="Document Id")],
        update_body_request: Passport,
        current_client: dict = Depends(get_current_client),
):
    owner = current_client["id"]
    return await print_request_service.update_by_id_and_document_type(
        str(print_request_id), update_body_request, DocumentType.PASSPORT, owner
    )


@router.put(
    "/id/{print_request_id}/document-type/accreditation",
    response_model=PrintRequest,
    status_code=status.HTTP_200_OK,
)
async def update_request_type_accreditation(
        print_request_id: Annotated[PydanticObjectId, Path(title="Document Id")],
        update_body_request: Accreditation,
        current_client: dict = Depends(get_current_client),
):
    owner = current_client["id"]

    return await print_request_service.update_by_id_and_document_type(
        str(print_request_id), update_body_request, DocumentType.ACCREDITATION, owner
    )


@router.put(
    "/id/{print_request_id}/document-type/dni",
    response_model=PrintRequest,
    status_code=status.HTTP_200_OK,
)
async def update_request_type_dni(
        print_request_id: Annotated[PydanticObjectId, Path(title="Document Id")],
        update_body_request: CardId,
        current_client: dict = Depends(get_current_client),
):
    owner = current_client["id"]

    return await print_request_service.update_by_id_and_document_type(
        str(print_request_id), update_body_request, DocumentType.DNI, owner
    )


@router.delete("/{id}", response_model=Any, status_code=status.HTTP_200_OK)
async def cancel_print_request(
        id: str, current_client: dict = Depends(get_current_client)
):
    owner = current_client["id"]

    return await print_request_service.cancel_print_request_by_id(id, owner)
