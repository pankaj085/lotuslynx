# backend/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # access token and authentication configuration
    SECRET_KEY: str = Field(
        default=...,
        min_length=32
    )
    ALGORITHM: str = Field(
        default="HS256"
    )
    ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(
        default=30
    )
    ACCESS_TOKEN_EXPIRES_DAYS: int = Field(
        default=30
    )
    REFRESH_TOKEN_EXPIRES_DAYS: int = Field(
        default=7
    )
    
    
    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME: str = Field(
        default=...,  
        description="Cloudinary cloud name from your dashboard"
    )
    CLOUDINARY_API_KEY: str = Field(
        default=...,  
        description="Cloudinary API Key from your dashboard"
    )
    CLOUDINARY_API_SECRET: str = Field(
        default=...,  
        description="Cloudinary API Secret from your dashboard"
    )
    

    # Stripe Configuration
    STRIPE_SECRET_KEY: str = Field(
        default=...,  
        description="Stripe Secret Key for API authentication"
    )
    STRIPE_WEBHOOK_SECRET: str = Field(
        default=...,  
        description="Stripe Webhook Secret for verifying webhook signatures"
    )
    STRIPE_CURRENCY: str = Field(
        default="usd",
        description="Default currency for Stripe payments"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Create settings instance
settings = Settings()