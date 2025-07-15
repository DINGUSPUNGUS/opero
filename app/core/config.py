"""
Production configuration management for Opero platform
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Production settings with validation"""
    
    # Application
    app_name: str = "Opero"
    app_version: str = "2.0.0"
    environment: str = "production"
    debug: bool = False
    secret_key: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_echo: bool = False
    
    # Redis
    redis_url: str
    redis_password: Optional[str] = None
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    email_from: str
    
    # Security
    allowed_hosts: List[str] = ["*"]
    cors_origins: List[str] = ["*"]
    https_only: bool = True
    secure_cookies: bool = True
    
    # AI Services
    openai_api_key: str
    ai_model: str = "gpt-4"
    ai_max_tokens: int = 4000
    ai_temperature: float = 0.7
    
    # Monitoring
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    analytics_key: Optional[str] = None
    
    # File Storage
    storage_type: str = "local"  # or 's3'
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Health Checks
    health_check_interval: int = 30
    database_health_check: bool = True
    redis_health_check: bool = True
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v
    
    @validator('jwt_secret_key')
    def validate_jwt_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters long')
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False
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

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Security middleware configuration
def get_security_headers():
    """Get security headers for production"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data: https:",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }


# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "logs/opero.log",
        },
        "error_file": {
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "logs/opero_errors.log",
            "level": "ERROR",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default", "file", "error_file"],
    },
}
