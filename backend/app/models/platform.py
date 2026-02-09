"""
Platform Model
Stores platform authentication credentials and session data
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import uuid
import enum

from app.db.base import Base, TimestampMixin


class PlatformType(str, enum.Enum):
    GOOGLE_MEET = "google_meet"
    MICROSOFT_TEAMS = "microsoft_teams"
    ZOOM = "zoom"


class PlatformStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ERROR = "error"
    PENDING_2FA = "pending_2fa"


class Platform(Base, TimestampMixin):
    """Platform authentication and session storage"""
    
    __tablename__ = "platforms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Platform identification
    platform_type = Column(SQLEnum(PlatformType), nullable=False)
    email = Column(String(255), nullable=False)
    
    # OAuth fields (for Google/Microsoft)
    oauth_provider = Column(String(50))  # 'google', 'microsoft', None
    access_token = Column(Text)  # Encrypted OAuth access token
    refresh_token = Column(Text)  # Encrypted OAuth refresh token
    token_expires_at = Column(DateTime)
    
    # Traditional auth fields (for Zoom)
    encrypted_password = Column(Text)  # Encrypted password
    
    # Session storage
    browser_session_state = Column(JSON)  # Playwright storageState
    session_cookies = Column(JSON)  # Browser cookies
    
    # Status tracking
    status = Column(SQLEnum(PlatformStatus), default=PlatformStatus.INACTIVE)
    last_tested_at = Column(DateTime)
    session_valid_until = Column(DateTime)
    error_message = Column(Text)
    
    # 2FA tracking
    requires_2fa = Column(Boolean, default=False)
    two_fa_pending = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="platforms")
    
    def __repr__(self):
        return f"<Platform {self.platform_type.value} - {self.email}>"
