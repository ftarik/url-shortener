from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, List

class URLCreate(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")
    custom_alias: Optional[str] = Field(None, description="Custom short code", max_length=50)
    expires_at: Optional[datetime] = Field(None, description="Expiration datetime")
    
    @field_validator('custom_alias')
    def validate_custom_alias(cls, v):
        if v:
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Custom alias can only contain letters, numbers, hyphens, and underscores')
            if v.lower() in ['shorten', 'stats', 'qr', 'urls', 'health', 'docs', 'redoc', 'openapi.json']:
                raise ValueError('This alias is reserved')
        return v

class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    
    class Config:
        from_attributes = True

class URLListResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    
    class Config:
        from_attributes = True

class URLStats(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    referrers: Dict[str, int]
    user_agents: Dict[str, int]
    recent_clicks: List[Dict]
    
    class Config:
        from_attributes = True
