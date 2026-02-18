from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class TeamsMeetingSession(Base):
    __tablename__ = "teams_meeting_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_url = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    mic_enabled = Column(Boolean, default=False)
    camera_enabled = Column(Boolean, default=False)
    status = Column(String, default="pending")  # pending, launching, joined, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
