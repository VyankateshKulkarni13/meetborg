"""
Meeting API Endpoints
CRUD operations for meeting management with platform auto-detection
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.meeting import Meeting, MeetingStatus
from app.models.user import User
from app.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    PlatformDetectionResponse
)
from app.services.platform_detector import platform_detector
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new meeting with auto-detected platform
    """
    # Auto-detect platform from URL
    platform, meeting_code = platform_detector.detect_platform(meeting_data.url)
    
    # Validate URL
    if not platform_detector.is_valid_url(meeting_data.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid meeting URL. Could not detect a supported platform."
        )
    
    # Create meeting instance
    meeting = Meeting(
        url=meeting_data.url,
        platform=platform,
        meeting_code=meeting_code,
        title=meeting_data.title,
        scheduled_time=meeting_data.scheduled_time,
        duration_minutes=meeting_data.duration_minutes,
        purpose=meeting_data.purpose,
        user_id=current_user.id,  # UUID, not string
        status=MeetingStatus.SCHEDULED
    )
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return meeting


@router.get("", response_model=MeetingListResponse)
async def list_meetings(
    skip: int = 0,
    limit: int = 100,
    status_filter: MeetingStatus = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all meetings for the current user with optional filtering
    """
    # Base query
    query = select(Meeting).where(Meeting.user_id == current_user.id)
    
    # Apply status filter if provided
    if status_filter:
        query = query.where(Meeting.status == status_filter)
    
    # Order by scheduled time (upcoming first, then by created_at)
    query = query.order_by(
        Meeting.scheduled_time.asc().nullsfirst(),
        Meeting.created_at.desc()
    )
    
    # Get total count
    count_query = select(Meeting).where(Meeting.user_id == current_user.id)
    if status_filter:
        count_query = count_query.where(Meeting.status == status_filter)
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    meetings = result.scalars().all()
    
    return MeetingListResponse(
        meetings=meetings,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific meeting by ID
    """
    result = await db.execute(
        select(Meeting).where(
            and_(
                Meeting.id == meeting_id,
                Meeting.user_id == current_user.id
            )
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    return meeting


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    meeting_data: MeetingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing meeting
    """
    # Get meeting
    result = await db.execute(
        select(Meeting).where(
            and_(
                Meeting.id == meeting_id,
                Meeting.user_id == str(current_user.id)
            )
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    # Update fields
    update_data = meeting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)
    
    meeting.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(meeting)
    
    return meeting


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a meeting
    """
    result = await db.execute(
        select(Meeting).where(
            and_(
                Meeting.id == meeting_id,
                Meeting.user_id == str(current_user.id)
            )
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    await db.delete(meeting)
    await db.commit()


@router.post("/{meeting_id}/join")
async def trigger_join(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger joining a meeting (calls simple_join.py)
    """
    # Get meeting
    result = await db.execute(
        select(Meeting).where(
            and_(
                Meeting.id == meeting_id,
                Meeting.user_id == str(current_user.id)
            )
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    # Update status
    meeting.status = MeetingStatus.IN_PROGRESS
    meeting.join_attempted_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(meeting)
    
    # Trigger automation script based on platform
    import subprocess
    from pathlib import Path
    from app.models.meeting import PlatformType
    
    backend_dir = Path(__file__).parent.parent.parent.parent.parent
    
    # Select script based on platform
    if meeting.platform == PlatformType.GOOGLE_MEET:
        script_path = backend_dir / "simple_join.py"
        print(f"[INFO] Triggering Google Meet automation for: {meeting.url}")
    elif meeting.platform == PlatformType.ZOOM:
        script_path = backend_dir / "zoom_join.py"
        print(f"[INFO] Triggering Zoom automation for: {meeting.url}")
    elif meeting.platform == PlatformType.MICROSOFT_TEAMS:
        script_path = backend_dir / "teams_join.py"
        print(f"[INFO] Triggering Teams automation for: {meeting.url}")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Automation not supported for platform: {meeting.platform}"
        )
    
    try:
        if settings.BOT_MODE == "docker":
            # ── Docker mode: spin up bot-worker container ──────────────────────
            # One container per meeting. Auto-destroys on exit (--rm).
            # Chrome runs inside the container on a virtual display (Xvfb) with
            # virtual audio (PulseAudio) — reliable cross-platform capture.
            import os
            recordings_abs = os.path.abspath(settings.RECORDINGS_PATH)
            os.makedirs(recordings_abs, exist_ok=True)

            subprocess.Popen([
                "docker", "run", "--rm",
                # Pass meeting details as env vars
                "-e", f"MEETING_URL={meeting.url}",
                "-e", f"MEETING_ID={meeting_id}",
                "-e", f"PLATFORM={meeting.platform.value}",
                "-e", f"API_URL=http://host.docker.internal:8000/api/v1",
                "-e", f"API_SECRET={settings.INTERNAL_BOT_SECRET}",
                "-e", "VNC_ENABLED=false",
                "-e", "RECORD_VIDEO=true",
                # Mount local recordings folder into container
                "-v", f"{recordings_abs}:/recordings",
                # Allow container to reach host machine's backend API
                "--add-host", "host.docker.internal:host-gateway",
                # Container name = meeting ID (useful for `docker ps` visibility)
                "--name", f"meetborg-bot-{meeting_id[:8]}",
                settings.BOT_WORKER_IMAGE,
            ])
            print(f"[OK] Bot-worker container launched for meeting {meeting_id}")
        else:
            # ── Local mode: run join script directly (Windows dev default) ─────
            subprocess.Popen([
                "python", str(script_path),
                meeting.url,
                "--meeting-id", str(meeting_id),
                "--api-url", "http://localhost:8000/api/v1",
                "--api-secret", settings.INTERNAL_BOT_SECRET,
            ])
            print(f"[OK] Automation script launched: {script_path.name}")
    except Exception as e:

        print(f"[ERROR] Failed to launch automation script: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger automation: {str(e)}"
        )
    

    return {
        "message": "Join triggered successfully",
        "meeting_id": meeting_id,
        "url": meeting.url,
        "platform": meeting.platform
    }


@router.post("/{meeting_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_meeting(
    meeting_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Internal endpoint called by bot scripts when a meeting ends.
    Auth: Authorization: Bearer {INTERNAL_BOT_SECRET}
    No user session required.
    """
    # Validate internal secret
    expected = f"Bearer {settings.INTERNAL_BOT_SECRET}"
    if not authorization or authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal secret"
        )

    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found"
        )

    meeting.status = MeetingStatus.COMPLETED
    meeting.join_successful = "success"
    meeting.updated_at = datetime.utcnow()
    await db.commit()
    print(f"[OK] Meeting {meeting_id} marked COMPLETED by bot")


@router.post("/detect-platform", response_model=PlatformDetectionResponse)
async def detect_platform(url: str):
    """
    Detect platform from meeting URL (no authentication required)
    """
    platform, meeting_code = platform_detector.detect_platform(url)
    is_valid = platform_detector.is_valid_url(url)
    
    return PlatformDetectionResponse(
        platform=platform,
        meeting_code=meeting_code,
        is_valid=is_valid,
        message=f"Detected: {platform_detector.get_platform_name(platform)}" if is_valid else "Could not detect platform"
    )
