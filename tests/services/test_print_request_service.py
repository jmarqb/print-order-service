from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi import HTTPException
import pytest

from models.order import DocumentType
from models.print_request import CardId
from services.print_request.print_request_service import (
    cancel_print_request_by_id,
    create_print_request,
    generate_print_request_code,
    get_print_request,
    get_print_requests,
    get_requests_analytics_summary,
    update_by_id_and_document_type,
    get_value_from_last_code,
)


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_request_by_id",
    new_callable=AsyncMock,
)
async def test_get_print_request(mock_request, get_print_request_fixture):
    print_request_id = str(ObjectId())
    owner = str(ObjectId())

    mock_request.return_value = get_print_request_fixture
    response = await get_print_request(print_request_id, owner, None)
    mock_request.assert_called_once_with(print_request_id, owner, None)
    assert response == get_print_request_fixture


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_request_by_id",
    new_callable=AsyncMock,
)
async def test_get_print_request_with_document_type(
    mock_request, get_print_request_fixture
):
    print_request_id = str(ObjectId())
    owner = str(ObjectId())
    document_type = DocumentType.DNI

    mock_request.return_value = get_print_request_fixture
    response = await get_print_request(print_request_id, owner, document_type)
    mock_request.assert_called_once_with(print_request_id, owner, document_type)
    assert response["document_type"] == get_print_request_fixture["document_type"]


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_request_by_id",
    new_callable=AsyncMock,
)
async def test_get_print_request_not_found(mock_request):
    print_request_id = str(ObjectId())
    owner = str(ObjectId())

    mock_request.return_value = None
    with pytest.raises(HTTPException) as exec:
        await get_print_request(print_request_id, owner, None)

    mock_request.assert_called_once_with(print_request_id, owner, None)
    assert exec.value.status_code == 404
    assert exec.value.detail == f"Print request with id {print_request_id} not found"


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_request_by_id",
    new_callable=AsyncMock,
)
async def test_get_print_request_with_document_type_not_found(mock_request):
    print_request_id = str(ObjectId())
    owner = str(ObjectId())
    document_type = DocumentType.DNI

    mock_request.return_value = None
    with pytest.raises(HTTPException) as exec:
        await get_print_request(print_request_id, owner, document_type)

    mock_request.assert_called_once_with(print_request_id, owner, document_type)
    assert exec.value.status_code == 404
    assert (
        exec.value.detail
        == f"Print request with id {print_request_id} for document type {document_type} not found"
    )


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.count_print_requests",
    new_callable=AsyncMock,
)
@patch(
    "services.print_request.print_request_service.database.retrieve_print_requests",
    new_callable=AsyncMock,
)
async def test_get_print_requests_paginated(
    mock_retrieve_requests, mock_count_requests, get_print_request_fixture
):

    owner = str(ObjectId())
    param_page = 0
    param_limit = 0

    print_requets_list = [get_print_request_fixture, get_print_request_fixture]
    total_requests = len(print_requets_list)

    mock_retrieve_requests.return_value = print_requets_list
    mock_count_requests.return_value = total_requests

    response = await get_print_requests(param_page, param_limit, owner)

    expected_response = {
        "items": print_requets_list,
        "total": total_requests,
        "current_page": 1,
        "total_pages": 1,
    }

    assert response == expected_response
    mock_retrieve_requests.assert_awaited_once_with(0, 10, owner)
    mock_count_requests.assert_awaited_once_with(owner)


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.cancel_print_request",
    new_callable=AsyncMock,
)
@patch(
    "services.print_request.print_request_service.get_print_request",
    new_callable=AsyncMock,
)
async def test_cancel_print_request(
    mock_print_request, mock_cancel_print_request, get_print_request_fixture
):
    print_request_id = str(ObjectId())
    owner = str(ObjectId())

    mock_print_request.return_value = get_print_request_fixture

    response = await cancel_print_request_by_id(print_request_id, owner)
    assert response == {"acknowledge": True, "deleted_count": 1}

    mock_print_request.assert_awaited_once()

    mock_cancel_print_request.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.update_print_request",
    new_callable=AsyncMock,
)
@patch(
    "services.print_request.print_request_service.get_print_request",
    new_callable=AsyncMock,
)
async def test_update_by_id_and_document_type(
    mock_print_request, mock_update_print_request, get_print_request_fixture
):
    print_request_id = str(ObjectId())
    owner = str(ObjectId())
    document_type = DocumentType.DNI

    mock_print_request.return_value = get_print_request_fixture
    mock_update_print_request.return_value = get_print_request_fixture
    data: CardId = get_print_request_fixture["metadata"]

    response = await update_by_id_and_document_type(
        print_request_id, data, document_type, owner
    )

    assert response == get_print_request_fixture
    mock_print_request.assert_awaited_once_with(print_request_id, owner, document_type)
    mock_update_print_request.assert_awaited_once()


@pytest.mark.parametrize(
    "code, expected",
    [
        ("S01", 1),
        ("S05", 5),
        ("S09", 9),
        ("S10", 10),
        ("S25", 25),
        ("S50", 50),
    ],
)
def test_get_value_from_last_code(code, expected):
    result = get_value_from_last_code(code)
    assert result == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, "S01"),
        (5, "S05"),
        (9, "S09"),
        (10, "S10"),
        (25, "S25"),
        (50, "S50"),
    ],
)
def test_generate_print_request_code(value, expected):
    result = generate_print_request_code(value)

    assert result == expected


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_requests_analytics_summary",
    new_callable=AsyncMock,
)
async def test_get_requests_analytics_summary(mock_summary):
    owner = str(ObjectId())

    mock_response = {
        "client_app": "client-name",
        "total_requests": 111,
        "unprocess": 64,
        "processed": 47,
        "total_passport_requests": 49,
        "passport_requests_proccessed": 3,
        "passport_requests_unproccess": 46,
        "total_dni_requests": 20,
        "dni_requests_proccessed": 2,
        "dni_requests_unproccess": 18,
        "total_accreditation_requests": 42,
        "accreditation_requests_proccessed": 42,
        "accreditation_requests_unproccess": 0,
    }

    mock_summary.return_value = [mock_response]

    response = await get_requests_analytics_summary(owner)
    assert response == mock_response
    mock_summary.assert_awaited_once_with(owner)


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_requests_last_code",
    new_callable=AsyncMock,
)
@patch(
    "services.print_request.print_request_service.database.insert_print_request",
    new_callable=AsyncMock,
)
async def test_create_order_with_last_order(
    mock_insert_print_request,
    mock_get_last_print_request,
    get_print_request_fixture,
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())
    metadata = get_print_request_fixture["metadata"]

    last_request = MagicMock()
    last_request.code = "S05"

    mock_get_last_print_request.return_value = [last_request]
    mock_insert_print_request.return_value = get_print_request_fixture

    response = await create_print_request(document_type, metadata, owner)

    assert response == get_print_request_fixture

    request_data = mock_insert_print_request.call_args.args[0]
    assert request_data["code"] == "S06"

    assert request_data["owner"] == owner

    assert request_data["document_type"] == document_type

    mock_insert_print_request.assert_awaited_once()
    mock_get_last_print_request.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_requests_last_code",
    new_callable=AsyncMock,
)
@patch(
    "services.print_request.print_request_service.database.insert_print_request",
    new_callable=AsyncMock,
)
async def test_create_order_without_last_order(
    mock_insert_print_request,
    mock_get_last_print_request,
    get_print_request_fixture,
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())
    metadata = get_print_request_fixture["metadata"]

    mock_get_last_print_request.return_value = []
    mock_insert_print_request.return_value = get_print_request_fixture

    response = await create_print_request(document_type, metadata, owner)

    assert response == get_print_request_fixture

    request_data = mock_insert_print_request.call_args.args[0]
    assert request_data["code"] == "S01"

    assert request_data["owner"] == owner

    assert request_data["document_type"] == document_type

    mock_insert_print_request.assert_awaited_once()
    mock_get_last_print_request.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "services.print_request.print_request_service.database.get_print_requests_last_code",
    new_callable=AsyncMock,
)
async def test_create_print_request_reaches_code_limit(
    mock_get_last_print_request, get_print_request_fixture
):
    document_type = DocumentType.PASSPORT
    owner = str(ObjectId())
    metadata = get_print_request_fixture["metadata"]

    last_request = MagicMock()
    last_request.code = "S50"

    mock_get_last_print_request.return_value = [last_request]

    with pytest.raises(HTTPException) as exc_info:
        await create_print_request(
            document_type,
            metadata,
            owner,
        )

        assert exc_info.value.status_code == 400

        assert "You reach PS50 limit" in exc_info.value.detail

        mock_get_last_print_request.assert_awaited_once()
