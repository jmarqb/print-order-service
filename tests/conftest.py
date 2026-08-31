from bson import ObjectId
import pytest
from fastapi.testclient import TestClient
import pytest_asyncio
from app import app
from config.config import initiate_database


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    await initiate_database(stage="test")


@pytest.fixture
def get_order_fixture():
    return {
        "_id": str(ObjectId()),
        "date": "2026-08-22T00:00:00",
        "code": "PSP20260822001",
        "associated_print_requests": [
            str(ObjectId()),
            str(ObjectId()),
            str(ObjectId()),
        ],
        "print_requests_type": "PASSPORT",
        "print_requests_quantity": 3,
        "owner": str(ObjectId()),
    }


@pytest.fixture
def get_print_request_fixture():
    return {
        "_id": str(ObjectId()),
        "reception_date": "2026-08-23T00:00:00",
        "code": "S01",
        "document_type": "DNI",
        "metadata": {
            "number": "012546",
            "person_name": "Marcos",
            "address": {
                "main_street": "apolo",
                "between_streets": "aranguren y pocito",
                "number": 132,
                "municipality": "quintana roo",
                "state": "tulun",
            },
            "volume": 156,
            "folio": 321,
        },
        "processed": False,
        "associated_order": None,
        "owner": str(ObjectId()),
        "cancelled": False,
    }


@pytest.fixture
def get_client_app_fixture():
    return {
        "_id": str(ObjectId()),
        "name": "testname",
        "url": "www.testclient.com",
        "password": "$argon2id$v=hashed_token",
        "active": True,
    }
