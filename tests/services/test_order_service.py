from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi import HTTPException
import pytest

from models.order import DocumentType
from models.print_request import PrintRequest
from services.order.order_service import (
    create_order,
    generate_order_code,
    get_order,
    get_orders,
    get_value_from_last_code,
)


@pytest.mark.asyncio
@patch("services.order.order_service.database.get_order_by_id", new_callable=AsyncMock)
async def test_get_order(mock_order, get_order_fixture):
    order_id = str(ObjectId())
    owner = str(ObjectId())

    mock_order.return_value = get_order_fixture
    response = await get_order(order_id, owner)
    mock_order.assert_called_once_with(order_id, owner)
    assert response == get_order_fixture


@pytest.mark.asyncio
@patch("services.order.order_service.database.get_order_by_id", new_callable=AsyncMock)
async def test_get_order_not_found(mock_order):
    order_id = str(ObjectId())
    owner = str(ObjectId())

    mock_order.return_value = None
    with pytest.raises(HTTPException) as exec:
        await get_order(order_id, owner)

    mock_order.assert_called_once_with(order_id, owner)
    assert exec.value.status_code == 404
    assert exec.value.detail == f"Order with id {order_id} not found"


@pytest.mark.asyncio
@patch(
    "services.order.order_service.database.count_print_orders", new_callable=AsyncMock
)
@patch("services.order.order_service.database.retrieve_orders", new_callable=AsyncMock)
async def test_get_orders_paginated(
        mock_retrieve_orders, mock_count_orders, get_order_fixture
):
    owner = str(ObjectId())
    param_page = 0
    param_limit = 0

    order_list = [get_order_fixture, get_order_fixture]
    total_orders = len(order_list)

    mock_retrieve_orders.return_value = order_list
    mock_count_orders.return_value = total_orders

    response = await get_orders(param_page, param_limit, owner)

    expected_response = {
        "items": order_list,
        "total": total_orders,
        "current_page": 1,
        "total_pages": 1,
    }

    assert response == expected_response
    mock_retrieve_orders.assert_awaited_once_with(0, 10, owner)
    mock_count_orders.assert_awaited_once_with(owner)


@pytest.mark.asyncio
@patch(
    "services.order.order_service.database.get_orders_last_code",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.retrieve_print_requests_unprocess",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.insert_order",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.update_unprocess_requests_to_process",
    new_callable=AsyncMock,
)
async def test_create_order_with_last_order(
        mock_update_requests,
        mock_insert_order,
        mock_retrieve_requests,
        mock_get_last_order,
        get_order_fixture,
        get_print_request_fixture,
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())

    date = datetime.now()
    date_format = date.strftime("%Y%m%d")

    last_order = MagicMock()
    last_order.code = "PSP20260827005"

    mock_get_last_order.return_value = [last_order]

    request = PrintRequest(**get_print_request_fixture)

    mock_retrieve_requests.return_value = [
        request,
        request,
    ]

    mock_insert_order.return_value = get_order_fixture

    response = await create_order(
        document_type=document_type,
        owner=owner,
    )

    assert response == get_order_fixture

    order_data = mock_insert_order.call_args.args[0]

    assert order_data["code"] == f"PSP{date_format}006"

    assert order_data["owner"] == owner

    assert order_data["print_requests_type"] == document_type

    assert order_data["print_requests_quantity"] == 2

    mock_get_last_order.assert_awaited_once()

    mock_retrieve_requests.assert_awaited_once_with(
        owner,
        document_type,
    )

    mock_insert_order.assert_awaited_once()

    mock_update_requests.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "services.order.order_service.database.get_orders_last_code",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.retrieve_print_requests_unprocess",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.insert_order",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.update_unprocess_requests_to_process",
    new_callable=AsyncMock,
)
async def test_create_order_without_last_order(
        mock_update_requests,
        mock_insert_order,
        mock_retrieve_requests,
        mock_get_last_order,
        get_order_fixture,
        get_print_request_fixture,
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())

    date = datetime.now()

    format_date = date.strftime("%Y%m%d")

    mock_get_last_order.return_value = []

    request = PrintRequest(**get_print_request_fixture)

    mock_retrieve_requests.return_value = [
        request,
    ]

    mock_insert_order.return_value = get_order_fixture

    response = await create_order(
        document_type=document_type,
        owner=owner,
    )

    assert response == get_order_fixture

    order_data = mock_insert_order.call_args.args[0]

    assert order_data["code"] == f"PSP{format_date}001"

    assert order_data["owner"] == owner

    assert order_data["print_requests_type"] == document_type

    assert order_data["print_requests_quantity"] == 1

    mock_get_last_order.assert_awaited_once()

    mock_retrieve_requests.assert_awaited_once_with(
        owner,
        document_type,
    )

    mock_insert_order.assert_awaited_once()

    mock_update_requests.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "services.order.order_service.database.get_orders_last_code",
    new_callable=AsyncMock,
)
async def test_create_order_reaches_code_limit(
        mock_get_last_order,
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())

    last_order = MagicMock()
    last_order.code = "PSP20260827999"

    mock_get_last_order.return_value = [last_order]

    with pytest.raises(HTTPException) as exc_info:
        await create_order(
            document_type=document_type,
            owner=owner,
        )

    assert exc_info.value.status_code == 400

    assert "You reach PSP20260827999 limit" in exc_info.value.detail

    mock_get_last_order.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "services.order.order_service.database.get_orders_last_code",
    new_callable=AsyncMock,
)
@patch(
    "services.order.order_service.database.retrieve_print_requests_unprocess",
    new_callable=AsyncMock,
)
async def test_create_order_without_print_requests(
        mock_retrieve_requests,
        mock_get_last_order,
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())

    mock_get_last_order.return_value = []

    mock_retrieve_requests.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        await create_order(
            document_type=document_type,
            owner=owner,
        )

    assert exc_info.value.status_code == 400

    assert exc_info.value.detail == (
        f"Not found print requests for type {document_type} "
        "to process - create order not proceed"
    )

    mock_get_last_order.assert_awaited_once()

    mock_retrieve_requests.assert_awaited_once_with(
        owner,
        document_type,
    )


@pytest.mark.parametrize(
    "code, expected",
    [
        ("PSP20260827001", 1),
        ("PSP20260827005", 5),
        ("PSP20260827009", 9),
        ("PSP20260827010", 10),
        ("PSP20260827025", 25),
        ("PSP20260827099", 99),
        ("PSP20260827100", 100),
        ("PSP20260827999", 999),
    ],
)
def test_get_value_from_last_code(code, expected):
    result = get_value_from_last_code(code)

    assert result == expected


@pytest.mark.parametrize(
    "document_type, expected_prefix",
    [
        (DocumentType.PASSPORT, "PSP"),
        (DocumentType.DNI, "DNI"),
        (DocumentType.ACCREDITATION, "ADC"),
    ],
)
def test_generate_order_code_prefix(
        document_type,
        expected_prefix,
):
    date = datetime(2026, 8, 27)

    result = generate_order_code(
        document_type=document_type,
        date=date,
        value=1,
    )

    assert result == f"{expected_prefix}20260827001"


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, "001"),
        (5, "005"),
        (9, "009"),
        (10, "010"),
        (25, "025"),
        (99, "099"),
        (100, "100"),
        (999, "999"),
    ],
)
def test_generate_order_code_value_format(
        value,
        expected,
):
    date = datetime(2026, 8, 27)

    result = generate_order_code(
        document_type=DocumentType.PASSPORT,
        date=date,
        value=value,
    )

    assert result == f"PSP20260827{expected}"
