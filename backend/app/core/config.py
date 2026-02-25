"""
Application Configuration
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Application
    APP_NAME: str = "AI Meeting Automation"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    # Internal secret used by bot scripts to call the /complete endpoint
    INTERNAL_BOT_SECRET: str = "meetborg-internal-secret-change-me"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: Optional[str] = None
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Hugging Face
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # n8n
    N8N_WEBHOOK_BASE_URL: Optional[str] = None
    
    # Bot Credentials
    GOOGLE_BOT_EMAIL: Optional[str] = None
    GOOGLE_BOT_PASSWORD: Optional[str] = None
    
    # File Storage
    RECORDINGS_PATH: str = "./recordings"
    MAX_RECORDING_SIZE_GB: int = 50
    
    # Session Security
    SESSION_EXPIRE_HOURS: int = 24
    ENCRYPTION_KEY: str
    
    # WebSocket
    WS_PORT: int = 8001
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Processing
    MAX_CONCURRENT_BOTS: int = 3
    TRANSCRIPTION_MODEL: str = "medium.en"
    GPU_ENABLED: bool = False
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_TENANT_ID: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = None
    
    class Config:
        env_file = "../.env"  # Look in parent directory
        case_sensitive = True


# Global settings instance
settings = Settings()
