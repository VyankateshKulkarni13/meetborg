from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TeamsSessionCreate(BaseModel):
    meeting_url: str
    display_name: str
    mic_enabled: bool
    camera_enabled: bool
    audio_input_device: Optional[str] = None
    audio_output_device: Optional[str] = None
    video_device: Optional[str] = None

class TeamsSessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
