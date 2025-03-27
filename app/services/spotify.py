"""Spotify service for interacting with the Spotify Web API."""
from typing import Dict, List, Any, Optional
import logging
import aiohttp
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service for interacting with Spotify Web API."""

    def __init__(self, access_token: str):
        """Initialize with access token."""
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to Spotify API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status == 401:
                        raise HTTPException(status_code=401, detail="Spotify token expired")
                    elif response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Spotify API error: {await response.text()}"
                        )
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Spotify API request failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to communicate with Spotify")

    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user's profile."""
        return await self._make_request("GET", "me")

    async def get_recently_played(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's recently played tracks."""
        params = {"limit": min(limit, 50)}  # Spotify max limit is 50
        data = await self._make_request("GET", "me/player/recently-played", params=params)
        return data.get("items", [])
