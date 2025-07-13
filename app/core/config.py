"""
Application configuration settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "AirAiBE API"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost/airai_be"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # AI settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Email settings
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # CORS settings
    allowed_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
