from datetime import datetime

from pydantic import BaseModel


class AccreditationPeriod(BaseModel):
    start_date: datetime
    end_date: datetime
