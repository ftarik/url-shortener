from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List


class URLCreate(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = Field(None, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class AnalyticsEntry(BaseModel):
    visited_at: datetime
    user_agent: Optional[str]
    ip_address: Optional[str]
    referer: Optional[str]

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    url_info: URLResponse
    total_clicks: int
    analytics: List[AnalyticsEntry]

    class Config:
        from_attributes = True
