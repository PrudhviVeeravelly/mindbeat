"""Service for interacting with the Spotify API."""

import logging
from typing import Dict, List, Any, Optional
import aiohttp
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service for interacting with the Spotify API."""

    def __init__(self, access_token: str):
        """Initialize the service.
        
        Args:
            access_token: Spotify access token
        """
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Spotify API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, params=params) as response:
                    if response.status == 401:
                        logger.error("Spotify token expired")
                        raise HTTPException(status_code=401, detail="Spotify token expired")
                    elif response.status != 200:
                        logger.error(f"Spotify API error: {response.status}")
                        error_data = await response.json()
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_data.get("error", {}).get("message", "Unknown error")
                        )
                    
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Network error in Spotify request: {str(e)}", exc_info=True)
            raise HTTPException(status_code=503, detail="Unable to reach Spotify")

    async def get_current_user(self) -> Dict[str, Any]:
        """Get the current user's profile."""
        try:
            logger.info("Fetching current user profile")
            return await self._make_request("GET", "me")
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}", exc_info=True)
            raise

    async def get_recently_played_tracks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the user's recently played tracks.
        
        Args:
            limit: Number of tracks to return (max 50)
            
        Returns:
            List of track objects
        """
        try:
            logger.info(f"Fetching {limit} recently played tracks")
            data = await self._make_request(
                "GET",
                "me/player/recently-played",
                params={"limit": min(limit, 50)}
            )
            return data.get("items", [])
        except Exception as e:
            logger.error(f"Error fetching recent tracks: {str(e)}", exc_info=True)
            return []

    async def get_audio_features(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """Get audio features for tracks.
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            List of audio feature objects
        """
        if not track_ids:
            return []

        try:
            logger.info(f"Fetching audio features for {len(track_ids)} tracks")
            data = await self._make_request(
                "GET",
                f"audio-features",
                params={"ids": ",".join(track_ids)}
            )
            return data.get("audio_features", [])
        except Exception as e:
            logger.error(f"Error fetching audio features: {str(e)}", exc_info=True)
            return []
