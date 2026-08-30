from unittest.mock import AsyncMock, patch

from bson import ObjectId
from fastapi import HTTPException
import pytest

MOCK_USER = str(ObjectId())


def override_get_current_client():
    return MOCK_USER


@pytest.mark.asyncio
@patch("routes.auth.auth_service.save_client", new_callable=AsyncMock)
async def test_register(mock_create_client, test_client):
    body = {
        "name": "test_client",
        "url": "www.cliente1.com",
        "password": 123456,
    }
    created_client_with_password = {
        "_id": str(ObjectId()),
        "name": body["name"],
        "url": body["url"],
        "active": True,
        "password": str(body["password"]),
    }

    mock_create_client.return_value = created_client_with_password

    response = test_client.post("/ms-print/api/v1/auth/signup", json=body)
    assert response.status_code == 201
    assert response.json() == created_client_with_password

    mock_create_client.assert_awaited_once()
    args, _ = mock_create_client.call_args
    assert args[0] == body["name"]
    assert args[1] == body["url"]
    assert args[2] == str(body["password"])


@pytest.mark.asyncio
@patch("routes.auth.auth_service.save_client", new_callable=AsyncMock)
async def test_register_already_exist_client(mock_create_client, test_client):
    body = {
        "name": "test_client",
        "url": "www.cliente1.com",
        "password": 123456,
    }

    mock_create_client.side_effect = HTTPException(
        status_code=400, detail=f"Name {body['name']} already exists"
    )

    response = test_client.post("/ms-print/api/v1/auth/signup", json=body)
    assert response.status_code == 400
    assert response.json() == {"detail": f"Name {body['name']} already exists"}


@pytest.mark.asyncio
@patch("routes.auth.auth_service.save_client", new_callable=AsyncMock)
async def test_register_error_invalid_body_url(mock_create_client, test_client):
    body = {
        "name": "test_client",
        "url": 5,  # invalid value should be a string,
        "password": 123456,
    }

    mock_create_client.side_effect = ValueError

    response = test_client.post("/ms-print/api/v1/auth/signup", json=body)
    assert response.status_code == 422

    type_data = response.json()["detail"][0]["type"]
    msg = response.json()["detail"][0]["msg"]
    assert msg == "Input should be a valid string"
    assert type_data == "string_type"
