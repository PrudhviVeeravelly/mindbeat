"""Core configuration module."""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Project settings
    PROJECT_NAME: str = "MindBeat"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Deployment settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    USE_HTTPS: bool = True
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*.railway.app"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    SESSION_COOKIE_NAME: str = "mindbeat_session"
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60  # 14 days in seconds
    
    # Spotify API settings
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: Optional[str] = None
    
    # Session settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Redis settings
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Sentry settings
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = ENVIRONMENT
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    class Config:
        """Pydantic settings config."""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in .env
        
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT.lower() == "production"
        
    def validate_spotify_credentials(self) -> bool:
        """Validate that Spotify credentials are set."""
        return bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET)
        
    def get_spotify_redirect_uri(self) -> str:
        """Get the appropriate Spotify redirect URI based on environment."""
        if self.SPOTIFY_REDIRECT_URI:
            return self.SPOTIFY_REDIRECT_URI
        
        scheme = "https" if self.USE_HTTPS else "http"
        host = "localhost:8000" if not self.is_production else self.ALLOWED_HOSTS[2].replace("*.", "")
        return f"{scheme}://{host}/auth/callback"

settings = Settings()
