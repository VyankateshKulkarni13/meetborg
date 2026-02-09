"""
Pydantic Schemas for Platform
Request and response models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum


class PlatformType(str, Enum):
    GOOGLE_MEET = "google_meet"
    MICROSOFT_TEAMS = "microsoft_teams"
    ZOOM = "zoom"


class PlatformStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ERROR = "error"
    PENDING_2FA = "pending_2fa"


class PlatformBase(BaseModel):
    """Base platform schema"""
    platform_type: PlatformType
    email: str


class PlatformCreate(PlatformBase):
    """Create platform account"""
    password: Optional[str] = None  # Required for Zoom, optional for OAuth


class PlatformUpdate(BaseModel):
    """Update platform account"""
    password: Optional[str] = None
    email: Optional[str] = None


class PlatformResponse(PlatformBase):
    """Platform response"""
    id: uuid.UUID
    user_id: uuid.UUID
    status: PlatformStatus
    oauth_provider: Optional[str] = None
    last_tested_at: Optional[datetime] = None
    session_valid_until: Optional[datetime] = None
    error_message: Optional[str] = None
    requires_2fa: bool = False
    two_fa_pending: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlatformListResponse(BaseModel):
    """List of platforms"""
    platforms: list[PlatformResponse]
    total: int


class TestConnectionResponse(BaseModel):
    """Connection test result"""
    success: bool
    status: PlatformStatus
    message: str
    session_valid_until: Optional[datetime] = None
