"""Authentication routes and utilities for the MindBeat application."""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SCOPES = [
    "user-read-email",
    "user-read-private",
    "user-read-recently-played",
    "user-read-currently-playing",
    "user-top-read"
]

def get_token_info(request: Request) -> Optional[Dict[str, Any]]:
    """Get token info from session."""
    token_info = request.session.get("token_info")
    
    if not token_info:
        return None
        
    # Check if token needs refresh
    now = datetime.now()
    expires_at = datetime.fromtimestamp(token_info.get("expires_at", 0))
    
    if expires_at <= now:
        # Token expired, try to refresh
        token_info = refresh_token(token_info.get("refresh_token"))
        if token_info:
            # Update session with new token info
            request.session["token_info"] = token_info
        else:
            # Refresh failed, clear session
            request.session.clear()
            return None
            
    return token_info

def refresh_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Refresh an expired access token."""
    if not refresh_token:
        return None
        
    try:
        response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.SPOTIFY_CLIENT_ID,
                "client_secret": settings.SPOTIFY_CLIENT_SECRET
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Token refresh failed: {response.text}")
            return None
            
        token_info = response.json()
        token_info["expires_at"] = int((
            datetime.now() + timedelta(seconds=token_info["expires_in"])
        ).timestamp())
        
        # Keep the refresh token if not provided in response
        if "refresh_token" not in token_info:
            token_info["refresh_token"] = refresh_token
            
        return token_info
        
    except requests.RequestException as e:
        logger.error(f"Token refresh error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return None

@router.get("/login")
async def login(request: Request):
    """Initiate Spotify OAuth flow."""
    try:
        if not settings.validate_spotify_credentials():
            raise HTTPException(
                status_code=500,
                detail="Spotify credentials not configured"
            )
            
        # Generate and store state
        state = secrets.token_urlsafe(32)
        request.session["spotify_auth_state"] = {
            "value": state,
            "timestamp": int((datetime.now() + timedelta(hours=1)).timestamp())
        }
        
        # Construct authorization URL
        params = {
            "response_type": "code",
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "scope": " ".join(SPOTIFY_SCOPES),
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "state": state
        }
        
        # Convert params to query string
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{SPOTIFY_AUTH_URL}?{query}"
        
        return RedirectResponse(auth_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initiate Spotify login"
        )

@router.get("/callback")
async def callback(request: Request, code: str, state: str):
    """Handle Spotify OAuth callback."""
    try:
        if not settings.validate_spotify_credentials():
            raise HTTPException(
                status_code=500,
                detail="Spotify credentials not configured"
            )
            
        # Verify state
        stored_state = request.session.get("spotify_auth_state")
        if not stored_state or stored_state["value"] != state:
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )
            
        # Clear stored state
        request.session.pop("spotify_auth_state", None)
        
        # Exchange code for tokens
        response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                "client_id": settings.SPOTIFY_CLIENT_ID,
                "client_secret": settings.SPOTIFY_CLIENT_SECRET
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange authorization code"
            )
            
        # Store token info in session
        token_info = response.json()
        token_info["expires_at"] = int((
            datetime.now() + timedelta(seconds=token_info["expires_in"])
        ).timestamp())
        
        request.session["token_info"] = token_info
        logger.info("Token info saved to session")
        
        return RedirectResponse("/")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to complete authentication"
        )

@router.get("/logout")
async def logout(request: Request, response: Response):
    """Log out the user by clearing their session."""
    try:
        # Clear session
        request.session.clear()
        
        # Clear session cookie
        response.delete_cookie(
            key=settings.SESSION_COOKIE_NAME,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="lax"
        )
        
        return RedirectResponse("/")
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to log out"
        )
