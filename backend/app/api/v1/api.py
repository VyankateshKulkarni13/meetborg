"""
API Router
Aggregates all API v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, platforms

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["Platforms"])

# Future routers (to be uncommented as implemented)
# api_router.include_router(personas.router, prefix="/personas", tags=["Personas"])
# api_router.include_router(missions.router, prefix="/missions", tags=["Missions"])
# api_router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])

# Placeholder health endpoint
@api_router.get("/ping")
async def ping():
    return {"message": "pong"}
