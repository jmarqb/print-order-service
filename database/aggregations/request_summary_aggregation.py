def get_request_summary_aggregation_pipeline():
    return [
        {"$match": {"cancelled": False}},
        {
            "$lookup": {
                "from": "clientapps",
                "localField": "owner",
                "foreignField": "_id",
                "as": "clients",
            }
        },
        {"$unwind": {"path": "$clients"}},
        {
            "$group": {
                "_id": {"client": "$clients.name"},
                "total_requests": {"$sum": 1},
                "unprocess": {
                    "$sum": {"$cond": [{"$eq": ["$processed", False]}, 1, 0]}
                },
                "processed": {"$sum": {"$cond": [{"$eq": ["$processed", True]}, 1, 0]}},
                "total_passport_requests": {
                    "$sum": {"$cond": [{"$eq": ["$document_type", "PASSPORT"]}, 1, 0]}
                },
                "passport_requests_proccessed": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$document_type", "PASSPORT"]},
                                    {"$eq": ["$processed", True]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "passport_requests_unproccess": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$document_type", "PASSPORT"]},
                                    {"$eq": ["$processed", False]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "total_dni_requests": {
                    "$sum": {"$cond": [{"$eq": ["$document_type", "DNI"]}, 1, 0]}
                },
                "dni_requests_proccessed": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$document_type", "DNI"]},
                                    {"$eq": ["$processed", True]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "dni_requests_unproccess": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$document_type", "DNI"]},
                                    {"$eq": ["$processed", False]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "total_accreditation_requests": {
                    "$sum": {
                        "$cond": [{"$eq": ["$document_type", "ACCREDITATION"]}, 1, 0]
                    }
                },
                "accreditation_requests_proccessed": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$document_type", "ACCREDITATION"]},
                                    {"$eq": ["$processed", True]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "accreditation_requests_unproccess": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$document_type", "ACCREDITATION"]},
                                    {"$eq": ["$processed", False]},
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "client_app": "$_id.client",
                "total_requests": 1,
                "unprocess": 1,
                "processed": 1,
                "total_passport_requests": 1,
                "passport_requests_proccessed": 1,
                "passport_requests_unproccess": 1,
                "total_dni_requests": 1,
                "dni_requests_proccessed": 1,
                "dni_requests_unproccess": 1,
                "total_accreditation_requests": 1,
                "accreditation_requests_proccessed": 1,
                "accreditation_requests_unproccess": 1,
            }
        },
        {"$sort": {"client_app": 1}},
    ]
