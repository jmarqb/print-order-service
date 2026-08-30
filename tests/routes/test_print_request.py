import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from models.order import DocumentType
from models.print_request import Passport
from routes.auth import get_current_client
from app import app
from fastapi import HTTPException, exceptions

MOCK_USER = {"id": str(ObjectId())}


def override_get_current_client():
    return MOCK_USER


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.get_print_requests",
    new_callable=AsyncMock,
)
async def test_get_print_requests_success(
    mock_get_requests, get_print_request_fixture, test_client
):
    app.dependency_overrides[get_current_client] = override_get_current_client

    mock_paginated_response = {
        "items": [
            get_print_request_fixture,
            get_print_request_fixture,
        ],
        "total": 121,
        "current_page": 1,
        "total_pages": 61,
    }

    mock_get_requests.return_value = mock_paginated_response

    response = test_client.get("/ms-print/api/v1/requests/?page=1&limit=10")

    assert response.status_code == 200
    assert response.json() == mock_paginated_response

    mock_get_requests.assert_awaited_once()
    args, _ = mock_get_requests.call_args
    assert args[0] == 1
    assert args[1] == 10
    assert str(args[2]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.get_print_request",
    new_callable=AsyncMock,
)
async def test_get_request_by_id_success(
    mock_get_request, get_print_request_fixture, test_client
):
    app.dependency_overrides[get_current_client] = override_get_current_client

    mock_response = get_print_request_fixture

    mock_get_request.return_value = mock_response
    print_request_id = ObjectId()

    response = test_client.get(f"/ms-print/api/v1/requests/{print_request_id}")

    assert response.status_code == 200
    assert response.json() == mock_response

    mock_get_request.assert_awaited_once()
    args, _ = mock_get_request.call_args
    assert args[0] == str(print_request_id)
    assert str(args[1]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.get_print_request",
    new_callable=AsyncMock,
)
async def test_get_request_by_id_not_found(mock_get_request, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    print_request_id = ObjectId()

    mock_get_request.side_effect = HTTPException(
        status_code=404, detail=f"Print request with id {id} not found"
    )

    response = test_client.get(f"/ms-print/api/v1/requests/{print_request_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Print request with id {id} not found"}

    mock_get_request.assert_awaited_once()
    args, _ = mock_get_request.call_args
    assert args[0] == str(print_request_id)
    assert str(args[1]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.get_print_request",
    new_callable=AsyncMock,
)
async def test_get_request_by_invalid_id(mock_get_request, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    print_request_id = "invalid-id"

    mock_get_request.side_effect = ValueError

    response = test_client.get(f"/ms-print/api/v1/requests/{print_request_id}")

    assert response.status_code == 422
    msg = response.json()["detail"][0]["msg"]
    assert msg == "Value error, Id must be of type PydanticObjectId"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.create_print_request",
    new_callable=AsyncMock,
)
async def test_create_order_success(
    mock_create_request, get_print_request_fixture, test_client
):
    app.dependency_overrides[get_current_client] = override_get_current_client

    document_type = DocumentType.PASSPORT
    metadata = {
        "number": "test-number",
        "person_name": "test-name",
        "city_birth": "test-city",
        "country_birth": "test-country",
    }
    body = {"document_type": document_type, "metadata": metadata}

    created_print_request = get_print_request_fixture

    mock_create_request.return_value = created_print_request

    response = test_client.post("/ms-print/api/v1/requests", json=body)

    assert response.status_code == 201
    assert response.json() == created_print_request

    mock_create_request.assert_awaited_once()
    args, _ = mock_create_request.call_args
    assert args[0] == body["document_type"]
    assert args[1] == Passport(**metadata)
    assert str(args[2]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.create_print_request",
    new_callable=AsyncMock,
)
async def test_create_request_invalid_document_type(mock_create_request, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    document_type = "other_document_type"
    body = {"document_type": document_type}

    mock_create_request.side_effect = ValueError

    response = test_client.post("/ms-print/api/v1/requests", json=body)

    assert response.status_code == 422

    type_data = response.json()["detail"][0]["type"]
    msg = response.json()["detail"][0]["msg"]
    assert msg == "Input should be 'PASSPORT', 'DNI' or 'ACCREDITATION'"
    assert type_data == "enum"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.cancel_print_request_by_id",
    new_callable=AsyncMock,
)
async def test_cancel_request_success(mock_get_request, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    mock_response = {"acknowledge": True, "deleted_count": 1}

    mock_get_request.return_value = mock_response
    print_request_id = ObjectId()

    response = test_client.delete(f"/ms-print/api/v1/requests/{print_request_id}")

    assert response.status_code == 200
    assert response.json() == mock_response

    mock_get_request.assert_awaited_once()
    args, _ = mock_get_request.call_args
    assert args[0] == str(print_request_id)
    assert str(args[1]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.cancel_print_request_by_id",
    new_callable=AsyncMock,
)
async def test_cancel_request_not_found(mock_get_request, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    print_request_id = ObjectId()

    mock_get_request.side_effect = HTTPException(
        status_code=404, detail=f"Print request with id {print_request_id} not found"
    )

    response = test_client.delete(f"/ms-print/api/v1/requests/{print_request_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Print request with id {print_request_id} not found"
    }

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch(
    "routes.print_request.print_request_service.update_by_id_and_document_type",
    new_callable=AsyncMock,
)
async def test_update_request_type_passport(
    mock_request, get_print_request_fixture, test_client
):
    app.dependency_overrides[get_current_client] = override_get_current_client

    print_request_id = ObjectId()
    document_type = DocumentType.PASSPORT

    body_update_passport = {
        "number": "test-number",
        "person_name": "test-name",
        "city_birth": "test-city",
        "country_birth": "test-country",
    }

    updated_print_request = get_print_request_fixture

    mock_request.return_value = updated_print_request

    response = test_client.put(
        f"/ms-print/api/v1/requests/id/{print_request_id}/document-type/passport",
        json=body_update_passport,
    )

    assert response.status_code == 200
    assert response.json() == updated_print_request

    app.dependency_overrides.clear()
