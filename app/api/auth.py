"""Authentication routes for the application."""

from typing import Optional
import logging
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.auth import create_spotify_oauth

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/login")
async def login(request: Request):
    """Initiate Spotify OAuth flow."""
    if not settings.validate_spotify_credentials():
        logger.error("Spotify credentials not configured")
        return JSONResponse(
            status_code=500,
            content={"error": "Spotify credentials not configured"}
        )

    try:
        auth = create_spotify_oauth()
        auth_url = auth.get_authorize_url()
        logger.info(f"Redirecting to Spotify auth URL: {auth_url}")
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error in login: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/callback")
async def callback(request: Request, code: Optional[str] = None, error: Optional[str] = None):
    """Handle Spotify OAuth callback."""
    if error:
        logger.error(f"Spotify auth error: {error}")
        return JSONResponse(
            status_code=400,
            content={"error": error}
        )

    if not code:
        logger.error("No authorization code provided")
        return JSONResponse(
            status_code=400,
            content={"error": "No authorization code provided"}
        )

    try:
        auth = create_spotify_oauth()
        token_info = auth.get_access_token(code)
        logger.info("Successfully obtained Spotify access token")
        
        # Store token in session
        request.session["access_token"] = token_info["access_token"]
        request.session["refresh_token"] = token_info["refresh_token"]
        request.session["token_expiry"] = str(token_info["expires_at"])

        logger.info("Token info stored in session, redirecting to dashboard")
        return RedirectResponse(url="/")
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/logout")
async def logout(request: Request, response: Response):
    """Log out the user by clearing their session."""
    request.session.clear()
    logger.info("User logged out successfully")
    return RedirectResponse(url="/")
