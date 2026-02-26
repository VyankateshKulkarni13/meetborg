"""
Meeting Schemas - Pydantic models for API request/response
"""
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from app.models.meeting import PlatformType, MeetingStatus


# Request schemas
class MeetingCreate(BaseModel):
    """Schema for creating a new meeting"""
    url: str = Field(..., description="Meeting URL")
    title: str = Field(..., min_length=1, max_length=200, description="Meeting title")
    scheduled_time: Optional[datetime] = Field(None, description="When the meeting is scheduled")
    duration_minutes: int = Field(60, ge=1, le=480, description="Meeting duration in minutes")
    purpose: Optional[str] = Field(None, max_length=1000, description="Meeting purpose/description")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format"""
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        v = v.strip()
        if not (v.startswith('http://') or v.startswith('https://')):
            v = 'https://' + v
        return v
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        """Ensure scheduled time is not in the past"""
        if v and v < datetime.now(timezone.utc):
            raise ValueError('Scheduled time cannot be in the past')
        return v.astimezone(timezone.utc).replace(tzinfo=None) if v else None


class MeetingUpdate(BaseModel):
    """Schema for updating an existing meeting"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    purpose: Optional[str] = Field(None, max_length=1000)
    status: Optional[MeetingStatus] = None
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        """Ensure scheduled time is not in the past"""
        if v and v < datetime.now(timezone.utc):
            raise ValueError('Scheduled time cannot be in the past')
        return v.astimezone(timezone.utc).replace(tzinfo=None) if v else None


# Response schemas
class MeetingResponse(BaseModel):
    """Schema for meeting response"""
    id: str
    url: str
    platform: PlatformType
    meeting_code: Optional[str]
    title: str
    scheduled_time: Optional[datetime]
    duration_minutes: int
    purpose: Optional[str]
    status: MeetingStatus
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    join_attempted_at: Optional[datetime]
    join_successful: Optional[str]
    recording_path: Optional[str] = None
    audio_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema for list of meetings"""
    meetings: list[MeetingResponse]
    total: int
    page: int
    page_size: int


class PlatformDetectionResponse(BaseModel):
    """Schema for platform detection response"""
    platform: PlatformType
    meeting_code: Optional[str]
    is_valid: bool
    message: Optional[str]
