import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId

from app import app
from routes.auth import get_current_client

MOCK_USER = {"id": str(ObjectId())}


def override_get_current_client():
    return MOCK_USER


@pytest.mark.asyncio
@patch(
    "routes.analytic.print_request_service.get_requests_analytics_summary",
    new_callable=AsyncMock,
)
async def test_get_print_request_summary_success(mock_get_summary, test_client):
    app.dependency_overrides[get_current_client] = override_get_current_client

    mock_summary_response = {
        "client_app": "name_client",
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

    mock_get_summary.return_value = mock_summary_response

    response = test_client.get("/ms-print/api/v1/analytics/requests-summary")

    assert response.status_code == 200
    assert response.json() == mock_summary_response

    mock_get_summary.assert_awaited_once()
    args, _ = mock_get_summary.call_args
    assert str(args[0]) == MOCK_USER["id"]
