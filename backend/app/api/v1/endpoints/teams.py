from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import subprocess
import sys
import platform
from pathlib import Path
from datetime import datetime

from app.db.session import get_db
from app.models.teams_session import TeamsMeetingSession
from app.schemas.teams import TeamsSessionCreate, TeamsSessionResponse

router = APIRouter()

@router.post("/join-session", response_model=TeamsSessionResponse)
async def join_teams_session(
    session_data: TeamsSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a Teams meeting session with specific configuration
    """
    # 1. Create session record
    session = TeamsMeetingSession(
        meeting_url=session_data.meeting_url,
        display_name=session_data.display_name,
        mic_enabled=session_data.mic_enabled,
        camera_enabled=session_data.camera_enabled,
        status="launching"
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    # 2. Launch Bot
    backend_dir = Path(__file__).parent.parent.parent.parent.parent
    bot_path = backend_dir / "app" / "services" / "bot" / "teams.py"
    
    # Construct arguments
    python_exe = sys.executable
    args = [
        python_exe, 
        str(bot_path), 
        session_data.meeting_url,
        "--name", session_data.display_name
    ]
    
    if session_data.mic_enabled:
        args.append("--mic")
    
    if session_data.camera_enabled:
        args.append("--camera")
        
    print(f"[TEAMS] Launching bot with args: {args}")
    
    try:
        if platform.system() == "Windows":
             # Use CREATE_NEW_CONSOLE for visibility per user preference
             CREATE_NEW_CONSOLE = 0x00000010
             subprocess.Popen(args, creationflags=CREATE_NEW_CONSOLE, close_fds=False)
        else:
             subprocess.Popen(args)
             
        session.status = "launched"
        await db.commit()
        
    except Exception as e:
        print(f"[ERROR] Failed to launch Teams bot: {e}")
        session.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to launch bot: {str(e)}")

    return session
