from bson import ObjectId
from pydantic import BaseModel
import pytest
from unittest.mock import AsyncMock, patch
from routes.auth import get_current_client
from app import app

MOCK_USER = {"id": str(ObjectId())}


def override_get_current_client():
    return MOCK_USER


class Token(BaseModel):
    access_token: str
    token_type: str


@pytest.mark.asyncio
@patch("routes.auth.auth_service.authenticate_client", new_callable=AsyncMock)
@patch("routes.auth.auth_service.create_access_token", return_value=Token)
async def test_login(mock_token, mock_client, test_client):
    mock_client_response = {
        "_id": MOCK_USER,
        "name": "minombre",
        "url": "www.minombre.com",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$kyFPcNihqdKqef+bgefefS$ZmqPVAAbjpMooeQVcSMO/o85Jrxakn9CPSt9vJyjIVQ",
        "active": True,
    }
    mock_token_response = "valid-token"

    mock_client.return_value = mock_client_response

    mock_token.return_value = mock_token_response

    response = test_client.post(
        "/ms-print/api/v1/auth/login", data={"username": "user", "password": "password"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == mock_token_response
    assert response.json()["token_type"] == "bearer"

    mock_client.assert_awaited_once_with("user", "password")
    mock_token.assert_called_with(mock_client_response)


@pytest.mark.asyncio
@patch("routes.auth.auth_service.authenticate_client", new_callable=AsyncMock)
async def test_login(mock_client, test_client):
    mock_client_response = False

    mock_client.return_value = mock_client_response

    response = test_client.post(
        "/ms-print/api/v1/auth/login", data={"username": "user", "password": "password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

    mock_client.assert_awaited_once_with("user", "password")


@pytest.mark.asyncio
async def test_read_client_me_success(test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    response = test_client.get(
        "/ms-print/api/v1/auth/client/me",
        headers={"WWW-Authenticate": "Bearer", "token": "any-token"},
    )

    assert response.status_code == 200
    assert response.json() == MOCK_USER

    app.dependency_overrides.clear()
