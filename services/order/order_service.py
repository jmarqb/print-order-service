from datetime import datetime
from math import ceil

from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import HTTPException, status
from database import database
from models.order import Order
from schemas.document_type import DocumentType


async def get_orders(page: int, limit: int, owner: str):
    page = 1 if page < 1 else page
    limit = 10 if limit < 1 else limit
    offset = (page - 1) * limit

    orders_list = await database.retrieve_orders(offset, limit, owner)
    total = await database.count_print_orders(owner)
    total_pages = ceil(total / limit)
    return {
        "items": orders_list,
        "total": total,
        "current_page": page,
        "total_pages": total_pages,
    }


async def get_order(id: str, owner: str) -> Order:
    order = await database.get_order_by_id(id, owner)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found",
        )
    return order


async def create_order(document_type: str, owner: str) -> Order:
    now = datetime.now()
    date = datetime(now.year, now.month, now.day)

    list_with_last_order = await database.get_orders_last_code(
        document_type, owner, date
    )
    code = ""
    if len(list_with_last_order) != 0:
        last_code_value = list_with_last_order[0].code
        value = get_value_from_last_code(last_code_value)
        if value < 999:
            code = generate_order_code(document_type, date, value + 1)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You reach {last_code_value} limit for the orders of type {document_type}, please process all pending print requests and create a order for reset the limit",
            )
    else:
        code = generate_order_code(document_type, date, 1)

    unproccess_print_request_list = await database.retrieve_print_requests_unprocess(
        owner, document_type
    )
    if len(unproccess_print_request_list) != 0:
        associated_print_requests = [
            PydanticObjectId(elem.id) for elem in unproccess_print_request_list
        ]

        print_requests_quantity = len(associated_print_requests)

        order_data = {
            "id": ObjectId(),
            "date": date,
            "code": code,
            "owner": owner,
            "print_requests_type": document_type,
            "associated_print_requests": associated_print_requests,
            "print_requests_quantity": print_requests_quantity,
        }

        created_order = await database.insert_order(order_data)
        await database.update_unprocess_requests_to_process(
            associated_print_requests, created_order
        )
        return created_order
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not found print requests for type {document_type} to process - create order not proceed",
        )


def get_value_from_last_code(value: str):
    # PSP20250101001 - PSP20250101999
    # DNI20250101001 - DNI20250101999
    # ADC20250101001 - ADC20250101999
    extract_value = value[11:]  # 001 - 999
    format_value = extract_value.removeprefix("0").removeprefix("0")
    return int(format_value)


def generate_order_code(document_type: str, date: datetime, value: int):
    prefix = "PSP"
    if document_type == DocumentType.DNI:
        prefix = "DNI"
    elif document_type == DocumentType.ACCREDITATION:
        prefix = "ADC"
    format_date = date.strftime("%Y%m%d")
    final_value = str(value)
    if 1 <= value <= 9:
        final_value = f"00{value}"
    elif 10 <= value <= 99:
        final_value = f"0{value}"
    code = "".join([prefix, format_date, final_value])
    return code
