from typing import Any
from math import ceil
from datetime import datetime
from fastapi import HTTPException, status

from bson import ObjectId
from database import database
from schemas import Passport, Accreditation, CardId, DocumentType, RequestSummaryResponse


async def get_print_requests(page: int, limit: int, owner: str):
    page = 1 if page < 1 else page
    limit = 10 if limit < 1 else limit
    offset = (page - 1) * limit

    print_requests_list = await database.retrieve_print_requests(offset, limit, owner)
    total = await database.count_print_requests(owner)
    total_pages = ceil(total / limit)
    return {
        "items": print_requests_list,
        "total": total,
        "current_page": page,
        "total_pages": total_pages,
    }


async def get_print_request(id: str, owner: str, document_type: str = None):
    print_request = await database.get_print_request_by_id(id, owner, document_type)
    if not print_request and not document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Print request with id {id} not found",
        )
    if not print_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Print request with id {id} for document type {document_type} not found",
        )
    return print_request


async def cancel_print_request_by_id(id: str, owner: str):
    print_request = await get_print_request(id, owner)
    await database.cancel_print_request(print_request)
    return {"acknowledge": True, "deleted_count": 1}


async def create_print_request(
        document_type: str, metadata: dict[str, Any], owner: str
) -> Any:
    now = datetime.now()
    reception_date = datetime(now.year, now.month, now.day)

    list_with_last_print_request = await database.get_print_requests_last_code(
        document_type, owner
    )
    code = ""
    if len(list_with_last_print_request) != 0:
        last_code_value = list_with_last_print_request[0].code
        value = get_value_from_last_code(last_code_value)
        if value < 50:
            code = generate_print_request_code(value + 1)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You reach {last_code_value} limit for the print-requests of type {document_type}, please process all pending print requests and create a order for reset the limit",
            )
    else:
        code = generate_print_request_code(1)
    print_request_data = {
        "id": ObjectId(),
        "reception_date": reception_date,
        "code": code,
        "owner": owner,
        "document_type": document_type,
        "metadata": metadata,
    }

    return await database.insert_print_request(print_request_data)


async def update_by_id_and_document_type(
        print_request_id: str,
        data: Passport | Accreditation | CardId,
        document_type: DocumentType,
        owner: str,
):
    print_request = await get_print_request(print_request_id, owner, document_type)

    return await database.update_print_request(print_request, data)


def get_value_from_last_code(value: str):
    # value = "S01 - S50"
    format_value = value.removeprefix("S").removeprefix("0")
    return int(format_value)


def generate_print_request_code(last_suffix: int):
    prefix = "S"
    prefix_decimal = "S0"
    if 1 <= last_suffix <= 9:
        return prefix_decimal + str(last_suffix)
    else:
        return prefix + str(last_suffix)


async def get_requests_analytics_summary(owner: str) -> RequestSummaryResponse:
    summary = await database.get_requests_analytics_summary(owner)
    result = summary[0] if summary.__len__() > 0 else RequestSummaryResponse(**{"client_app": str(owner)})
    return result
