"""Main application module."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
    openapi_url="/api/openapi.json" if not settings.is_production else None
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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

@app.get("/")
def root():
    """Root endpoint."""
    return {"status": "ok"}

# Import routers after app creation to avoid circular imports
from app.api import auth, frontend
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(frontend.router, tags=["frontend"])
