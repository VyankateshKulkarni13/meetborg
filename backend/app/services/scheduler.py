"""
Meeting Auto-Join Scheduler
Polls database for upcoming meetings and triggers the join bot
"""
import asyncio
import subprocess
import sys
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import AsyncSessionLocal as SessionLocal
from app.models.meeting import Meeting, MeetingStatus

logger = logging.getLogger(__name__)

# Config
POLL_INTERVAL_SECONDS = 30
JOIN_BUFFER_SECONDS = 60  # Join 60 seconds before scheduled time
MAX_JOIN_ATTEMPTS = 3

class AutoJoinScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            self.check_upcoming_meetings,
            IntervalTrigger(seconds=POLL_INTERVAL_SECONDS),
            id='check_meetings',
            replace_existing=True
        )
        self.running_processes = {}  # meeting_id: subprocess

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Auto-join scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Auto-join scheduler stopped")

    async def check_upcoming_meetings(self):
        """
        Check for meetings that need to be joined
        """
        logger.info("Checking for upcoming meetings...")
        
        async with SessionLocal() as db:
            try:
                # Calculate time window
                now = datetime.utcnow()
                join_window_start = now
                join_window_end = now + timedelta(seconds=JOIN_BUFFER_SECONDS)
                
                # Query meetings that are:
                # 1. Scheduled
                # 2. Start within buffer window OR started recently but missed
                # 3. Have not been joined yet
                query = select(Meeting).where(
                    and_(
                        Meeting.status == MeetingStatus.SCHEDULED,
                        Meeting.scheduled_time <= join_window_end,
                        # Don't join meetings that are too old (e.g. > 15 mins past start)
                        Meeting.scheduled_time >= now - timedelta(minutes=15)
                    )
                )
                
                result = await db.execute(query)
                meetings = result.scalars().all()
                
                for meeting in meetings:
                    await self.trigger_join(meeting, db)
                    
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")

    async def trigger_join(self, meeting: Meeting, db: AsyncSession):
        """
        Trigger the join bot for a specific meeting
        """
        meeting_id = meeting.id
        url = meeting.url
        title = meeting.title
        
        logger.info(f"Triggering auto-join for meeting: {title} ({url})")
        
        try:
            # Update status to IN_PROGRESS
            meeting.status = MeetingStatus.IN_PROGRESS
            meeting.join_attempted_at = datetime.utcnow()
            await db.commit()
            await db.refresh(meeting)
            
            # Launch join script as subprocess
            # We use subprocess.Popen to run it in background without blocking
            cmd = [sys.executable, "simple_join.py", url]
            
            # Note: In production, you might want to use a more robust task queue like Celery
            # But for this MVP, a subprocess is sufficient
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process reference (optional, for management)
            self.running_processes[meeting_id] = process
            
            logger.info(f"Join process started for {meeting_id} (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"Failed to trigger join for {meeting_id}: {e}")
            
            # Revert status or mark as failed
            meeting.status = MeetingStatus.FAILED
            meeting.join_successful = f"Failed to launch bot: {str(e)}"
            await db.commit()

# Global instance
scheduler = AutoJoinScheduler()
