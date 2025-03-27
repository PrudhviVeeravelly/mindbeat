"""Authentication utilities."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import spotipy

from app.core.config import settings

def create_spotify_oauth() -> spotipy.oauth2.SpotifyOAuth:
    """Create a SpotifyOAuth instance."""
    return spotipy.oauth2.SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.get_spotify_redirect_uri(),
        scope="user-read-recently-played user-read-private user-read-email"
    )

def get_token_info(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get token info from session."""
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    token_expiry = session.get("token_expiry")

    if not all([access_token, refresh_token, token_expiry]):
        return None

    expiry = datetime.fromtimestamp(float(token_expiry))
    if expiry <= datetime.now():
        # Token expired, try to refresh
        try:
            auth = create_spotify_oauth()
            token_info = auth.refresh_access_token(refresh_token)
            session["access_token"] = token_info["access_token"]
            session["refresh_token"] = token_info.get("refresh_token", refresh_token)
            session["token_expiry"] = str(token_info["expires_at"])
            return token_info
        except:
            return None

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": float(token_expiry)
    }
