from typing import List, Any
from datetime import datetime

from beanie import PydanticObjectId

from database.aggregations import request_summary_aggregation
from models import PrintRequest, Order, ClientApp
from schemas import Passport, Accreditation, CardId

print_request_collection = PrintRequest
order_collection = Order
client_app_collection = ClientApp


async def get_print_request_by_id(
        print_request_id: str,
        owner: PydanticObjectId,
        document_type: str = None,
) -> PrintRequest:
    filters = {
        "cancelled": False,
        "_id": PydanticObjectId(print_request_id),
        "owner": owner,
    }
    if document_type is not None:
        filters["document_type"] = document_type
    return await print_request_collection.find_one(filters)


async def update_print_request(
        print_request: PrintRequest, data: Passport | Accreditation | CardId
) -> PrintRequest:
    return await print_request_collection.update(
        print_request, {"$set": {"metadata": data}}
    )


async def cancel_print_request(data: PrintRequest) -> None:
    await print_request_collection.update(data, {"$set": {"cancelled": True}})


async def retrieve_print_requests(
        offset: int, limit: int, owner: str
) -> List[PrintRequest]:
    filters = {"cancelled": False, "owner": PydanticObjectId(owner)}
    print_requests = (
        await print_request_collection.find(filters).skip(offset).limit(limit).to_list()
    )
    return print_requests


async def retrieve_print_requests_unprocess(
        owner: str, document_type: str
) -> List[PrintRequest]:
    filters = {
        "cancelled": False,
        "processed": False,
        "owner": PydanticObjectId(owner),
        "document_type": document_type,
    }
    return await print_request_collection.find(filters).to_list()


async def update_unprocess_requests_to_process(
        ids_list: list[PydanticObjectId], order: Order
):
    filters = {"_id": {"$in": ids_list}}
    await print_request_collection.find(filters).update_many(
        {"$set": {"processed": True, "associated_order": PydanticObjectId(order.id)}}
    )


async def count_print_requests(owner: str) -> int:
    filters = {"cancelled": False, "owner": PydanticObjectId(owner)}
    count = await print_request_collection.find(filters).count()
    return count


async def get_print_requests_last_code(
        document_type: str, owner: str
) -> List[PrintRequest]:
    filters = {
        "cancelled": False,
        "processed": False,
        "document_type": document_type,
        "owner": PydanticObjectId(owner),
    }
    print_request_last_code = (
        await print_request_collection.find(filters)
        .sort(-PrintRequest.code)
        .limit(1)
        .to_list()
    )
    return print_request_last_code


async def insert_print_request(print_request_data: PrintRequest) -> PrintRequest:
    print_request_instance = PrintRequest(**print_request_data)
    created_request = await print_request_collection.insert_one(print_request_instance)
    return created_request


async def insert_client_app(client_app_data: ClientApp) -> ClientApp:
    client_app_instance = ClientApp(**client_app_data)
    created_client = await client_app_collection.insert_one(client_app_instance)
    del created_client.password
    return created_client


async def exists_client_app(client_app_name: str) -> bool:
    filters = {"active": True, "name": client_app_name}
    exists_client = await client_app_collection.find_one(filters)
    return False if not exists_client else True


async def get_client_app(client_app_name: str) -> ClientApp:
    filters = {"active": True, "name": client_app_name}
    return await client_app_collection.find_one(filters)


async def retrieve_orders(offset: int, limit: int, owner: str) -> List[Order]:
    filters = {"owner": PydanticObjectId(owner)}
    orders = await order_collection.find(filters).skip(offset).limit(limit).to_list()
    return orders


async def count_print_orders(owner: str) -> int:
    filters = {"owner": PydanticObjectId(owner)}
    count = await order_collection.find(filters).count()
    return count


async def get_orders_last_code(
        document_type: str, owner: str, date: datetime
) -> List[Order]:
    filters = {
        "print_requests_type": document_type,
        "owner": PydanticObjectId(owner),
        "date": date,
    }
    order_last_code = (
        await order_collection.find(filters).sort(-Order.code).limit(1).to_list()
    )
    return order_last_code


async def get_order_by_id(id: str, owner: str) -> Order:
    filters = {"_id": PydanticObjectId(id), "owner": PydanticObjectId(owner)}
    return await order_collection.find_one(filters)


async def insert_order(order_data: Order) -> Order:
    order_instance = Order(**order_data)
    created_order = await order_collection.insert_one(order_instance)
    return created_order


async def get_requests_analytics_summary(owner: str = None) -> List[Any]:
    pipeline = request_summary_aggregation.get_request_summary_aggregation_pipeline()
    if owner:
        pipeline.insert(0, {"$match": {"owner": PydanticObjectId(owner)}})
    return await print_request_collection.aggregate(pipeline).to_list()
