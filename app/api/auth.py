"""Authentication routes for the application."""

from typing import Optional
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.auth import create_spotify_oauth

router = APIRouter()

@router.get("/login")
async def login(request: Request):
    """Initiate Spotify OAuth flow."""
    if not settings.validate_spotify_credentials():
        return JSONResponse(
            status_code=500,
            content={"error": "Spotify credentials not configured"}
        )

    try:
        auth = create_spotify_oauth()
        auth_url = auth.get_authorize_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/callback")
async def callback(request: Request, code: Optional[str] = None, error: Optional[str] = None):
    """Handle Spotify OAuth callback."""
    if error:
        return JSONResponse(
            status_code=400,
            content={"error": error}
        )

    if not code:
        return JSONResponse(
            status_code=400,
            content={"error": "No authorization code provided"}
        )

    try:
        auth = create_spotify_oauth()
        token_info = auth.get_access_token(code)
        
        # Store token in session
        request.session["access_token"] = token_info["access_token"]
        request.session["refresh_token"] = token_info["refresh_token"]
        request.session["token_expiry"] = str(token_info["expires_at"])

        return RedirectResponse(url="/dashboard")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/logout")
async def logout(request: Request, response: Response):
    """Log out the user by clearing their session."""
    request.session.clear()
    return RedirectResponse(url="/")
