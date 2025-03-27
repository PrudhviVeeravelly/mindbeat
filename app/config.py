"""Application configuration module."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Project settings
    PROJECT_NAME: str = "MindBeat"
    VERSION: str = "1.0.0"
    
    # Spotify API settings
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # Session settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production!
    SESSION_COOKIE_NAME: str = "mindbeat_session"
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60  # 14 days in seconds
    
    # Token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        """Pydantic settings config."""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in .env

settings = Settings()
