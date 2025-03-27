"""Configuration settings."""
import logging
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "MindBeat"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    SESSION_COOKIE_NAME: str = "mindbeat_session"
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60  # 14 days in seconds

    # CORS
    _ALLOWED_HOSTS: str = "*"  # Store as comma-separated string

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Convert comma-separated string to list."""
        return [h.strip() for h in self._ALLOWED_HOSTS.split(",")]

    # Environment
    ENVIRONMENT: str = "development"
    _USE_HTTPS: str = "false"  # Store as string, convert in property

    @property
    def USE_HTTPS(self) -> bool:
        """Convert string to bool for USE_HTTPS."""
        return str(self._USE_HTTPS).lower() == "true"

    # Spotify API - Optional during startup
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: Optional[str] = None

    # Redis - Optional
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Sentry - Optional
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.ENVIRONMENT.lower() == "production"

    def get_spotify_redirect_uri(self) -> str:
        """Get the Spotify redirect URI based on environment."""
        if self.SPOTIFY_REDIRECT_URI:
            logger.info(f"Using configured redirect URI: {self.SPOTIFY_REDIRECT_URI}")
            return self.SPOTIFY_REDIRECT_URI
        
        scheme = "https" if self.USE_HTTPS else "http"
        host = "localhost:8000" if not self.is_production else self.ALLOWED_HOSTS[0].replace("*.", "")
        uri = f"{scheme}://{host}/auth/callback"
        logger.info(f"Generated redirect URI: {uri}")
        return uri

    def validate_spotify_credentials(self) -> bool:
        """Check if Spotify credentials are configured."""
        has_credentials = bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET)
        if not has_credentials:
            logger.error("Missing Spotify credentials")
            logger.error(f"SPOTIFY_CLIENT_ID set: {bool(self.SPOTIFY_CLIENT_ID)}")
            logger.error(f"SPOTIFY_CLIENT_SECRET set: {bool(self.SPOTIFY_CLIENT_SECRET)}")
        return has_credentials

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
        validate_default=False  # Don't validate default values
    )

# Create settings instance
settings = Settings(_env_file=None)

# Log initial configuration
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"HTTPS enabled: {settings.USE_HTTPS}")
logger.info(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
logger.info(f"Spotify credentials configured: {settings.validate_spotify_credentials()}")
logger.info(f"Spotify redirect URI: {settings.get_spotify_redirect_uri()}")
