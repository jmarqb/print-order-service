from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from pymongo import UpdateMany
import pytest

from database.aggregations import request_summary_aggregation
from database.database import (
    cancel_print_request,
    count_print_orders,
    count_print_requests,
    exists_client_app,
    get_client_app,
    get_order_by_id,
    get_orders_last_code,
    get_print_request_by_id,
    get_print_requests_last_code,
    get_requests_analytics_summary,
    insert_client_app,
    insert_order,
    insert_print_request,
    retrieve_orders,
    retrieve_print_requests,
    retrieve_print_requests_unprocess,
    update_print_request,
    update_unprocess_requests_to_process,
)
from models.client_app import ClientApp
from models.order import Order
from models.print_request import DocumentType, PrintRequest

request_id = str(ObjectId())
owner = str(ObjectId())


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find_one", new_callable=AsyncMock)
async def test_get_print_request_by_id(mock_print_request, get_print_request_fixture):

    mock_print_request.return_value = get_print_request_fixture
    result = await get_print_request_by_id(request_id, owner, None)

    assert result == get_print_request_fixture

    mock_print_request.assert_awaited_once()


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find_one", new_callable=AsyncMock)
async def test_get_print_request_by_id_with_document_type(
    mock_print_request, get_print_request_fixture
):

    mock_print_request.return_value = get_print_request_fixture
    result = await get_print_request_by_id(request_id, owner, DocumentType.DNI)

    assert result == get_print_request_fixture

    mock_print_request.assert_awaited_once()


@pytest.mark.asyncio
@patch("database.database.print_request_collection.update", new_callable=AsyncMock)
async def test_update_print_request(mock_update, get_print_request_fixture):
    print_request = MagicMock(PrintRequest)
    data = get_print_request_fixture["metadata"]

    mock_update.return_value = print_request

    result = await update_print_request(print_request, data)
    assert result == print_request

    mock_update.assert_awaited_once_with(print_request, {"$set": {"metadata": data}})


@pytest.mark.asyncio
@patch("database.database.print_request_collection.update", new_callable=AsyncMock)
async def test_cancell_print_request(mock_update):
    print_request = MagicMock(PrintRequest)
    mock_update.return_value = None

    result = await cancel_print_request(print_request)
    assert result == None

    mock_update.assert_awaited_once_with(print_request, {"$set": {"cancelled": True}})


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_retrieve_print_requests(mock_find):
    print_request = MagicMock(spec=PrintRequest)
    print_request.cancelled = False
    print_request.owner = ObjectId(owner)
    list_print_requests = [print_request, print_request]

    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    mock_cursor.to_list = AsyncMock(return_value=list_print_requests)

    mock_find.return_value = mock_cursor

    result = await retrieve_print_requests(2, 2, owner)
    assert result == list_print_requests

    mock_find.assert_called_once_with({"cancelled": False, "owner": ObjectId(owner)})
    mock_cursor.skip.assert_called_once_with(2)
    mock_cursor.limit.assert_called_once_with(2)
    mock_cursor.to_list.assert_called_once_with()


@pytest.mark.asyncio
@patch("database.database.order_collection.find")
async def test_retrieve_orders(mock_find):
    order = MagicMock(spec=Order)
    order.owner = owner
    list_orders = [order, order]

    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    mock_cursor.to_list = AsyncMock(return_value=list_orders)

    mock_find.return_value = mock_cursor

    result = await retrieve_orders(2, 2, owner)
    assert result == list_orders

    mock_find.assert_called_once_with({"owner": ObjectId(owner)})
    mock_cursor.skip.assert_called_once_with(2)
    mock_cursor.limit.assert_called_once_with(2)
    mock_cursor.to_list.assert_called_once_with()


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_retrieve_print_requests_unprocess(mock_find):
    document_type = DocumentType.DNI
    print_request = MagicMock(PrintRequest)
    print_request.processed = False
    print_request.document_type = document_type

    list_requests_unprocess = [print_request, print_request]
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=list_requests_unprocess)
    mock_find.return_value = mock_cursor

    result = await retrieve_print_requests_unprocess(owner, document_type)
    assert result.__len__ == list_requests_unprocess.__len__
    assert result[0].document_type == document_type
    assert result[1].document_type == document_type
    assert result[0].processed == False
    assert result[1].processed == False

    mock_find.assert_called_once()


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_update_unprocess_requests_to_process(mock_find, get_order_fixture):
    list_ids = [request_id, request_id]
    order = Order(**get_order_fixture)

    print_request = MagicMock(PrintRequest)

    list_requests_unprocess = [print_request, print_request]

    mock_update = MagicMock()
    mock_update.update_many = AsyncMock(return_value=list_requests_unprocess)
    mock_find.return_value = mock_update

    result = await update_unprocess_requests_to_process(list_ids, order)
    assert result == None

    mock_find.assert_called_once()


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_count_print_requests(mock_find):

    print_request = MagicMock(PrintRequest)

    list_requests_founded = [print_request, print_request]

    mock_count = MagicMock(int)
    mock_count.count = AsyncMock(return_value=list_requests_founded.__len__)
    mock_find.return_value = mock_count

    result = await count_print_requests(owner)
    assert result == list_requests_founded.__len__

    mock_find.assert_called_once()


@pytest.mark.asyncio
@patch("database.database.print_request_collection.insert_one")
async def test_insert_print_request(mock_insert_one, get_print_request_fixture):

    print_request = PrintRequest(**get_print_request_fixture)
    mock_insert_one.return_value = print_request
    result = await insert_print_request(get_print_request_fixture)
    assert result == print_request

    mock_insert_one.assert_awaited_once_with(print_request)


@pytest.mark.asyncio
@patch("database.database.client_app_collection.insert_one", new_callable=AsyncMock)
async def test_insert_client_app(mock_insert_one, get_client_app_fixture):

    client_app = ClientApp(**get_client_app_fixture)
    mock_insert_one.return_value = client_app
    result = await insert_client_app(get_client_app_fixture)
    assert result == client_app

    mock_insert_one.assert_awaited_once()


@pytest.mark.asyncio
@patch("database.database.client_app_collection.find_one", new_callable=AsyncMock)
async def test_exists_client_app(mock_find_one, get_client_app_fixture):

    client_name = str(get_client_app_fixture.get("name"))
    mock_find_one.return_value = get_client_app_fixture

    result = await exists_client_app(client_name)
    assert result == True

    mock_find_one.assert_awaited_once()


@pytest.mark.asyncio
@patch("database.database.client_app_collection.find_one", new_callable=AsyncMock)
async def test_get_client_app(mock_find_one, get_client_app_fixture):

    client_name = str(get_client_app_fixture.get("name"))
    mock_find_one.return_value = get_client_app_fixture

    result = await get_client_app(client_name)
    assert result == get_client_app_fixture

    mock_find_one.assert_awaited_once()


@pytest.mark.asyncio
@patch("database.database.order_collection.find")
async def test_count_print_orders(mock_find, get_order_fixture):

    order = MagicMock(Order)

    list_orders_founded = [order, order]

    mock_count = MagicMock(int)
    mock_count.count = AsyncMock(return_value=list_orders_founded.__len__)
    mock_find.return_value = mock_count

    result = await count_print_orders(owner)
    assert result == list_orders_founded.__len__

    mock_find.assert_called_once()


@pytest.mark.asyncio
@patch("database.database.order_collection.find_one", new_callable=AsyncMock)
async def test_get_order_by_id(mock_order, get_order_fixture):

    mock_order.return_value = get_order_fixture
    result = await get_order_by_id(request_id, owner)

    assert result == get_order_fixture

    mock_order.assert_awaited_once()


@pytest.mark.asyncio
@patch("database.database.order_collection.insert_one", new_callable=AsyncMock)
async def test_insert_order(mock_insert_one, get_order_fixture):

    order = Order(**get_order_fixture)
    mock_insert_one.return_value = order
    result = await insert_order(get_order_fixture)
    assert result == order

    mock_insert_one.assert_awaited_once()


# TODO: ESTUDIAR A DETALLE ESTA SECCION
@pytest.mark.asyncio
@patch("database.database.print_request_collection.aggregate")
async def test_get_requests_analytics_summary_without_owner(mock_aggregate):
    # Datos de prueba
    expected_result = [
        {"client_app": "Client1", "total_requests": 10, "processed": 7, "unprocess": 3},
        {"client_app": "Client2", "total_requests": 5, "processed": 2, "unprocess": 3},
    ]

    # Configurar el cursor de agregación (mismo patrón que find)
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=expected_result)
    mock_aggregate.return_value = mock_cursor

    # Ejecutar sin owner
    result = await get_requests_analytics_summary()

    # Verificar resultado
    assert result == expected_result

    # Verificar que aggregate fue llamado y obtener el pipeline usado
    mock_aggregate.assert_called_once()
    actual_pipeline = mock_aggregate.call_args[0][0]

    # Verificar que el pipeline base NO tiene el $match de owner al inicio
    assert actual_pipeline[0] == {"$match": {"cancelled": False}}
    assert "$lookup" in actual_pipeline[1]


@pytest.mark.asyncio
@patch("database.database.print_request_collection.aggregate")
async def test_get_requests_analytics_summary_with_owner(mock_aggregate):
    owner_id = "507f1f77bcf86cd799439011"
    expected_result = [{"client_app": "Client1", "total_requests": 5}]

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=expected_result)
    mock_aggregate.return_value = mock_cursor

    # Ejecutar CON owner
    result = await get_requests_analytics_summary(owner=owner_id)

    assert result == expected_result

    # Verificar que el pipeline tiene el $match de owner insertado al PRINCIPIO
    actual_pipeline = mock_aggregate.call_args[0][0]

    # El primer elemento debe ser el $match de owner
    assert actual_pipeline[0] == {"$match": {"owner": ObjectId(owner_id)}}
    # El segundo elemento es el $match original de cancelled
    assert actual_pipeline[1] == {"$match": {"cancelled": False}}


@pytest.mark.asyncio
@patch("database.database.print_request_collection.aggregate")
async def test_get_requests_analytics_summary_pipeline_structure(mock_aggregate):
    """
    Test que verifica la estructura completa del pipeline generado.
    """
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_aggregate.return_value = mock_cursor

    await get_requests_analytics_summary(owner="507f1f77bcf86cd799439011")

    pipeline = mock_aggregate.call_args[0][0]

    # Verificar etapas clave del pipeline
    assert pipeline[0]["$match"]["owner"]  # Filtro de owner insertado
    assert pipeline[1]["$match"]["cancelled"] == False
    assert pipeline[2]["$lookup"]["from"] == "clientapps"
    assert pipeline[3]["$unwind"]["path"] == "$clients"
    assert "$group" in pipeline[4]
    assert "$project" in pipeline[5]
    assert pipeline[6]["$sort"] == {"client_app": 1}


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_get_print_requests_last_code(mock_find):
    document_type = "PASSPORT"
    owner_id = "507f1f77bcf86cd799439011"

    # Mock con código realista "S50" (el último/más alto)
    mock_request = MagicMock()
    mock_request.code = "S50"
    mock_request.document_type = document_type
    expected_result = [mock_request]

    # Configurar mocks
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=expected_result)
    mock_find.return_value = mock_cursor

    result = await get_print_requests_last_code(document_type, owner_id)

    assert result == expected_result
    assert result[0].code == "S50"

    # Verificar filtros
    mock_find.assert_called_once_with(
        {
            "cancelled": False,
            "processed": False,
            "document_type": document_type,
            "owner": ObjectId(owner_id),
        }
    )

    # Verificar que se ordena por código descendente
    mock_cursor.sort.assert_called_once()
    sort_arg = mock_cursor.sort.call_args[0][0]
    # Si PrintRequest.code sobrecarga __neg__, verificar que es -PrintRequest.code
    # o simplemente verificar que se llamó con el campo correcto

    mock_cursor.limit.assert_called_once_with(1)


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_get_print_requests_last_code_returns_latest(mock_find):
    """Test que verifica que devuelve el código más alto (S50 vs S01)"""
    owner_id = owner

    mock_request = MagicMock()
    mock_request.code = "S50"  # El último código

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[mock_request])
    mock_find.return_value = mock_cursor

    result = await get_print_requests_last_code("DNI", owner_id)

    assert len(result) == 1
    assert result[0].code == "S50"


@pytest.mark.asyncio
@patch("database.database.print_request_collection.find")
async def test_get_print_requests_last_code_no_results(mock_find):
    """Test cuando no hay solicitudes pendientes"""
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[])  # Sin resultados

    mock_find.return_value = mock_cursor

    result = await get_print_requests_last_code("PASSPORT", "507f1f77bcf86cd799439011")

    assert result == []


@pytest.mark.asyncio
@patch("database.database.order_collection.find")
async def test_get_orders_last_code(mock_find):
    # Datos de prueba
    document_type = "PASSPORT"
    owner_id = "507f1f77bcf86cd799439011"
    test_date = datetime(2026, 8, 22, 10, 30, 0)

    # Mock con código realista "PSP20260822001" (el último sería "PSP20260822999")
    mock_order = MagicMock()
    mock_order.code = "PSP20260822999"  # El último código del día
    mock_order.print_requests_type = document_type
    mock_order.date = test_date
    expected_result = [mock_order]

    # Configurar cadena de mocks
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor  # sort() síncrono
    mock_cursor.limit.return_value = mock_cursor  # limit() síncrono
    mock_cursor.to_list = AsyncMock(return_value=expected_result)

    mock_find.return_value = mock_cursor

    # Ejecutar
    result = await get_orders_last_code(document_type, owner_id, test_date)

    # Verificar resultado
    assert result == expected_result
    assert result[0].code == "PSP20260822999"

    # Verificar filtros correctos
    expected_filters = {
        "print_requests_type": document_type,
        "owner": ObjectId(owner_id),
        "date": test_date,
    }
    mock_find.assert_called_once_with(expected_filters)

    # Verificar ordenamiento descendente por code y limit(1)
    mock_cursor.sort.assert_called_once()
    mock_cursor.limit.assert_called_once_with(1)
    mock_cursor.to_list.assert_called_once()


@pytest.mark.asyncio
@patch("database.database.order_collection.find")
async def test_get_orders_last_code_first_code_of_day(mock_find):
    """Test cuando es el primer código del día (001)"""
    test_date = datetime(2026, 8, 23)

    mock_order = MagicMock()
    mock_order.code = "PSP20260823001"  # Primer código del día 23

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[mock_order])
    mock_find.return_value = mock_cursor

    result = await get_orders_last_code("DNI", "507f1f77bcf86cd799439011", test_date)

    assert result[0].code == "PSP20260823001"


@pytest.mark.asyncio
@patch("database.database.order_collection.find")
async def test_get_orders_last_code_no_orders(mock_find):
    """Test cuando no hay órdenes para esa fecha/tipo/owner"""
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[])

    mock_find.return_value = mock_cursor

    result = await get_orders_last_code(
        "PASSPORT", "507f1f77bcf86cd799439011", datetime(2026, 8, 24)
    )

    assert result == []
    mock_find.assert_called_once_with(
        {
            "print_requests_type": "PASSPORT",
            "owner": ObjectId("507f1f77bcf86cd799439011"),
            "date": datetime(2026, 8, 24),
        }
    )
