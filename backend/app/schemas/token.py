"""
Token Schemas
JWT token request and response models
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[str] = None
