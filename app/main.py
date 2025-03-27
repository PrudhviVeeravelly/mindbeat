"""Main application module."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import auth, frontend
from app.core.config import settings
from app.core.logging_config import configure_logging

# Configure logging based on environment
configure_logging(settings.ENVIRONMENT)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Analyze your music listening habits and mood patterns"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=settings.USE_HTTPS
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(frontend.router, tags=["frontend"])

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info(
        "Starting MindBeat application",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
            "https_enabled": settings.USE_HTTPS,
            "allowed_hosts": settings.ALLOWED_HOSTS
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
