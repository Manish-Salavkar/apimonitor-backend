from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AnalyticsBase(BaseModel):
    api_id: int
    api_key_id: Optional[int]
    window_start: datetime
    window_end: datetime

    request_count: int
    success_count: int
    error_count: int
    rate_limit_exceeded_count: int

    avg_response_time_ms: int
    max_response_time_ms: int

    


class AnalyticsOut(AnalyticsBase):
    id: int

    class Config:
        from_attributes = True


class AnalyticsListResponse(BaseModel):
    data: List[AnalyticsOut]
    message: str


class ApiUserSummary(BaseModel):
    api_name: str
    unique_users: int
    total_calls: int

class UserActivityLog(BaseModel):
    username: str
    api_name: str
    total_calls: int
    last_called: datetime

class UserAnalyticsResponse(BaseModel):
    api_summary: List[ApiUserSummary]
    user_activity: List[UserActivityLog]