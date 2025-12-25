from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AnalyticsBase(BaseModel):
    api_id: str
    api_key_id: Optional[str]
    window_start: datetime
    window_end: datetime

    request_count: int
    success_count: int
    error_count: int
    rate_limit_exceeded_count: int

    avg_response_time_ms: int
    max_response_time_ms: int


class AnalyticsOut(AnalyticsBase):
    id: str

    class Config:
        from_attributes = True


class AnalyticsListResponse(BaseModel):
    data: List[AnalyticsOut]
    message: str
