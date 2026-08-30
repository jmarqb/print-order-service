from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi import HTTPException
import pytest

from models.client_app import ClientApp
from services.auth.auth_service import (
    authenticate_client,
    create_access_token,
    save_client,
    validate_token,
    verify_password,
)


@pytest.mark.asyncio
@patch("services.auth.auth_service.database.insert_client_app", new_callable=AsyncMock)
@patch("services.auth.auth_service.database.exists_client_app", new_callable=AsyncMock)
async def test_save_client_if_not_exist(mock_exist_client, mock_created_client):
    mock_exist_client.return_value = False

    mock_response = {
        "_id": str(ObjectId()),
        "name": "minombre",
        "url": "www.minombre.com",
        "active": True,
    }
    mock_created_client.return_value = mock_response

    response = await save_client(
        mock_response["name"], mock_response["url"], "any-password"
    )

    assert response == mock_response

    mock_exist_client.assert_awaited_once()
    mock_created_client.assert_awaited_once()


@pytest.mark.asyncio
@patch("services.auth.auth_service.database.exists_client_app", new_callable=AsyncMock)
async def test_save_client_raise_already_exist_client(mock_exist_client):
    mock_exist_client.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        await save_client("client-name", "client-url", "any-password")

    assert exc_info.value.status_code == 400

    assert "Name client-name already exists" in exc_info.value.detail
    mock_exist_client.assert_awaited_once()


@pytest.mark.asyncio
@patch("services.auth.auth_service.verify_password", return_value=bool)
@patch("services.auth.auth_service.database.get_client_app", new_callable=AsyncMock)
async def test_authenticate_client(mock_returned_client, mock_verify_password):
    client = MagicMock(ClientApp)

    mock_returned_client.return_value = client

    mock_verify_password.return_value = True

    response = await authenticate_client(client.name, client.password)
    assert response == client

    mock_returned_client.assert_awaited_once_with(client.name)
    mock_verify_password.assert_called_once()


@pytest.mark.asyncio
@patch("services.auth.auth_service.verify_password", return_value=bool)
@patch("services.auth.auth_service.database.get_client_app", new_callable=AsyncMock)
async def test_authenticate_client_invalid_password(
        mock_returned_client, mock_verify_password
):
    client = MagicMock(ClientApp)

    mock_returned_client.return_value = client

    mock_verify_password.return_value = False

    response = await authenticate_client(client.name, client.password)
    assert response == False

    mock_returned_client.assert_awaited_once_with(client.name)
    mock_verify_password.assert_called_once()


@pytest.mark.asyncio
@patch("services.auth.auth_service.verify_password", return_value=bool)
@patch("services.auth.auth_service.database.get_client_app", new_callable=AsyncMock)
async def test_authenticate_client_non_exist_client(
        mock_returned_client, mock_verify_password
):
    client = None

    mock_returned_client.return_value = client

    mock_verify_password.return_value = False

    response = await authenticate_client("name", "password")
    assert response == False

    mock_returned_client.assert_awaited_once_with("name")
    mock_verify_password.assert_called_once()


@patch("services.auth.auth_service.password_hash.verify", return_value=MagicMock(str))
def test_verify_password(return_mock):
    return_mock.return_value = True

    result = verify_password("plain_password", "hashed_passw")

    assert result == True


@patch("services.auth.auth_service.jwt.encode", return_value=MagicMock(str))
def test_create_access_token(jwt_encode):
    token = "fake-token"

    client = MagicMock(ClientApp)
    client.name = "fake-name"
    client.id = "fake-id"
    jwt_encode.return_value = token
    result = create_access_token(client)

    assert result == token


@patch("services.auth.auth_service.jwt.decode", return_value=MagicMock(dict))
def test_validate_token(jwt_decode):
    data = {
        "sub": "fake-name",
        "id": "fake-id",
        "issuer": "ms-fake",
        "expire": "any-time",
    }
    token = "fake-token"

    jwt_decode.return_value = data
    result = validate_token(token)

    assert result == data


def test_validate_token_invalid():
    with pytest.raises(HTTPException) as exc_info:
        validate_token("any-token")

    assert exc_info.value.status_code == 401

    assert "Token inválido o expirado" in exc_info.value.detail
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
