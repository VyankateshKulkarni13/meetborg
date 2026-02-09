"""
Platform API Endpoints
CRUD operations for platform authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.platform import Platform, PlatformType, PlatformStatus
from app.schemas.platform import (
    PlatformCreate,
    PlatformResponse,
    PlatformListResponse,
    TestConnectionResponse
)
from app.core.security import get_current_user
from app.core.encryption import encrypt_credential, decrypt_credential

router = APIRouter()


@router.get("", response_model=PlatformListResponse)
async def list_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all platforms for current user"""
    result = await db.execute(
        select(Platform).where(Platform.user_id == current_user.id)
    )
    platforms = result.scalars().all()
    
    return PlatformListResponse(
        platforms=platforms,
        total=len(platforms)
    )


@router.post("", response_model=PlatformResponse, status_code=status.HTTP_201_CREATED)
async def create_platform(
    platform_data: PlatformCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new platform account"""
    
    # Check if platform already exists for this user
    existing = await db.execute(
        select(Platform).where(
            Platform.user_id == current_user.id,
            Platform.platform_type == platform_data.platform_type,
            Platform.email == platform_data.email
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform account already exists"
        )
    
    # Create new platform
    platform = Platform(
        user_id=current_user.id,
        platform_type=platform_data.platform_type,
        email=platform_data.email,
        status=PlatformStatus.INACTIVE
    )
    
    # Encrypt and store password if provided
    if platform_data.password:
        platform.encrypted_password = encrypt_credential(platform_data.password)
    
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    
    return platform


@router.get("/{platform_id}", response_model=PlatformResponse)
async def get_platform(
    platform_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific platform"""
    result = await db.execute(
        select(Platform).where(
            Platform.id == platform_id,
            Platform.user_id == current_user.id
        )
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
    
    return platform


@router.delete("/{platform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform(
    platform_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a platform account"""
    result = await db.execute(
        select(Platform).where(
            Platform.id == platform_id,
            Platform.user_id == current_user.id
        )
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
    
    await db.delete(platform)
    await db.commit()


@router.post("/{platform_id}/test", response_model=TestConnectionResponse)
async def test_connection(
    platform_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test platform connection"""
    result = await db.execute(
        select(Platform).where(
            Platform.id == platform_id,
            Platform.user_id == current_user.id
        )
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
    
    # Instantiate service
    from app.services.browser_auth import BrowserAuthService
    auth_service = BrowserAuthService()
    
    # Decrypt password
    try:
        if not platform.encrypted_password:
             raise Exception("No password found")
        password = decrypt_credential(platform.encrypted_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Credential error: {str(e)}"
        )
    
    # Verify using Playwright
    success, message, session_data = await auth_service.verify_credentials(
        platform_type=platform.platform_type.value,
        email=platform.email,
        password=password
    )
    
    # Update platform status
    platform.last_tested_at = datetime.utcnow()
    
    if success:
        platform.status = PlatformStatus.ACTIVE
        platform.session_valid_until = datetime.utcnow() + timedelta(days=1)
        platform.error_message = None
        if session_data:
            platform.session_cookies = session_data.get('cookies')
    else:
        # Check if 2FA is required (future)
        platform.status = PlatformStatus.ERROR
        platform.error_message = message
    
    await db.commit()
    await db.refresh(platform)
    
    return TestConnectionResponse(
        success=success,
        status=platform.status,
        message=message,
        session_valid_until=platform.session_valid_until
    )
