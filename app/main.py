"""Main application module."""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A mood analysis app based on your Spotify listening history"
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=settings.SESSION_MAX_AGE
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Import routers after app creation to avoid circular imports
from app.api import auth, frontend  # noqa

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(frontend.router, tags=["frontend"])

@app.on_event("startup")
async def startup_event():
    """Log configuration on startup."""
    logger.info("Application starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"HTTPS enabled: {settings.USE_HTTPS}")
    logger.info(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    logger.info(f"Spotify credentials configured: {settings.validate_spotify_credentials()}")
    logger.info(f"Spotify redirect URI: {settings.get_spotify_redirect_uri()}")
