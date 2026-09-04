from typing import List, Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    current_page: int
    total_pages: int
