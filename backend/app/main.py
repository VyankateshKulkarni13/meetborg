"""
FastAPI Application Entry Point
Main application factory and configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base import Base
from app.services.scheduler import scheduler
# Import models so Base.metadata registers all tables BEFORE create_all runs
from app.models import User, Platform, Meeting  # noqa: F401



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Handles startup and shutdown logic
    """
    # Startup
    print("🚀 Starting AI Meeting Automation System...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    
    # Create database tables if they don't exist
    # In production, use Alembic migrations instead
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created")
    
    # Start scheduler
    scheduler.start()
    print("⏰ Auto-join scheduler started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Meeting Automation System...")
    scheduler.stop()
    print("zzz Scheduler stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Self-hosted meeting bot automation system with command center dashboard",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "redis": "connected"  # TODO: Add actual Redis health check
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
