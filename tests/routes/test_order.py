import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from models.order import DocumentType
from routes.auth import get_current_client
from app import app
from fastapi import HTTPException, exceptions

MOCK_USER = {"id": str(ObjectId())}


def override_get_current_client():
    return MOCK_USER


@pytest.mark.asyncio
@patch("routes.order.order_service.get_orders", new_callable=AsyncMock)
async def test_get_orders_success(mock_get_orders, test_client, get_order_fixture):
    app.dependency_overrides[get_current_client] = override_get_current_client

    mock_paginated_response = {
        "items": [
            get_order_fixture,
            get_order_fixture,
        ],
        "total": 3,
        "current_page": 1,
        "total_pages": 2,
    }

    mock_get_orders.return_value = mock_paginated_response

    response = test_client.get("/ms-print/api/v1/orders/?page=1&limit=10")

    assert response.status_code == 200
    assert response.json() == mock_paginated_response

    mock_get_orders.assert_awaited_once()
    args, _ = mock_get_orders.call_args
    assert args[0] == 1
    assert args[1] == 10
    assert str(args[2]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch("routes.order.order_service.get_order", new_callable=AsyncMock)
async def test_get_order_by_id_success(mock_get_order, test_client, get_order_fixture):
    app.dependency_overrides[get_current_client] = override_get_current_client

    mock_response = get_order_fixture

    mock_get_order.return_value = mock_response
    order_id = ObjectId(mock_response["_id"])

    response = test_client.get(f"/ms-print/api/v1/orders/{order_id}")

    assert response.status_code == 200
    assert response.json() == mock_response

    mock_get_order.assert_awaited_once()
    args, _ = mock_get_order.call_args
    assert args[0] == order_id
    assert str(args[1]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch("routes.order.order_service.get_order", new_callable=AsyncMock)
async def test_get_order_by_id_not_found(mock_get_order, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    order_id = ObjectId()
    mock_get_order.side_effect = HTTPException(
        status_code=404, detail=f"Order with id {order_id} not found"
    )

    response = test_client.get(f"/ms-print/api/v1/orders/{order_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Order with id {order_id} not found"}

    mock_get_order.assert_awaited_once()
    args, _ = mock_get_order.call_args
    assert args[0] == order_id
    assert str(args[1]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch("routes.order.order_service.get_order", new_callable=AsyncMock)
async def test_get_order_by_invalid_id(mock_get_order, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    order_id = "invalid_id"
    mock_get_order.side_effect = ValueError

    response = test_client.get(f"/ms-print/api/v1/orders/{order_id}")

    assert response.status_code == 422
    msg = response.json()["detail"][0]["msg"]
    assert msg == "Value error, Id must be of type PydanticObjectId"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch("routes.order.order_service.create_order", new_callable=AsyncMock)
async def test_create_order_success(mock_create_order, test_client, get_order_fixture):
    app.dependency_overrides[get_current_client] = override_get_current_client

    document_type = DocumentType.ACCREDITATION
    body = {"document_type": document_type}

    created_order = get_order_fixture

    mock_create_order.return_value = created_order

    response = test_client.post("/ms-print/api/v1/orders", json=body)

    assert response.status_code == 201
    assert response.json() == created_order

    mock_create_order.assert_awaited_once()
    args, _ = mock_create_order.call_args
    assert args[0] == body["document_type"]
    assert str(args[1]) == MOCK_USER["id"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch("routes.order.order_service.create_order", new_callable=AsyncMock)
async def test_create_order_invalid_document_type(mock_create_order, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    document_type = "other_document_type"
    body = {"document_type": document_type}

    mock_create_order.side_effect = ValueError

    response = test_client.post("/ms-print/api/v1/orders", json=body)

    assert response.status_code == 422

    type_data = response.json()["detail"][0]["type"]
    msg = response.json()["detail"][0]["msg"]
    assert msg == "Input should be 'PASSPORT', 'DNI' or 'ACCREDITATION'"
    assert type_data == "enum"

    app.dependency_overrides.clear()
