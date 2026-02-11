"""
Meeting Model
Stores meeting information with auto-detected platform
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base
import uuid


class PlatformType(str, enum.Enum):
    """Supported meeting platforms"""
    GOOGLE_MEET = "google_meet"
    ZOOM = "zoom"
    MICROSOFT_TEAMS = "microsoft_teams"
    WEBEX = "webex"
    JITSI = "jitsi"
    OTHER = "other"


class MeetingStatus(str, enum.Enum):
    """Meeting lifecycle status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Meeting(Base):
    """Meeting model with URL, platform detection, and scheduling"""
    
    __tablename__ = "meetings"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Meeting details
    url = Column(String, nullable=False, index=True)
    platform = Column(SQLEnum(PlatformType), nullable=False)
    meeting_code = Column(String, nullable=True)  # Extracted from URL
    
    # User-provided info
    title = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=True, index=True)
    duration_minutes = Column(Integer, default=60)
    purpose = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    
    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="meetings")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Join tracking
    join_attempted_at = Column(DateTime, nullable=True)
    join_successful = Column(String, nullable=True)  # Success/failure reason
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, platform={self.platform}, status={self.status})>"
