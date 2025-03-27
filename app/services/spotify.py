"""Spotify service for interacting with the Spotify Web API."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import HTTPException, Request

from app.core.config import settings
from app.schemas.mood import AudioFeatures
from app.api.auth import get_token_info

logger = logging.getLogger(__name__)

SPOTIFY_SCOPES = [
    "user-read-recently-played",
    "user-top-read",
    "user-read-currently-playing",
    "user-read-email",
    "user-read-private"
]

class SpotifyService:
    """Service for interacting with Spotify Web API."""
    
    def __init__(self, access_token: str):
        """Initialize the Spotify client.
        
        Args:
            access_token: Spotify access token
        """
        try:
            self.client = spotipy.Spotify(auth=access_token)
            logger.info("Successfully initialized Spotify client")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {str(e)}")
            raise
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get the current user's Spotify profile.
        
        Returns:
            Dict containing user profile information
        """
        try:
            return self.client.current_user()
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise
    
    async def get_recent_tracks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the user's recently played tracks with audio features.
        
        Args:
            limit: Maximum number of tracks to return
            
        Returns:
            List of track objects with audio features
        """
        try:
            # Get recently played tracks
            recent_tracks = self.client.current_user_recently_played(limit=limit)
            
            if not recent_tracks or not recent_tracks['items']:
                logger.info("No recent tracks found")
                return []
            
            # Extract track IDs and basic info
            tracks = []
            for item in recent_tracks['items']:
                track = item['track']
                tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms']
                })
            
            # Get audio features for all tracks
            track_ids = [t['id'] for t in tracks]
            features = self.client.audio_features(track_ids)
            
            # Combine track info with audio features
            for track, feature in zip(tracks, features):
                if feature:  # Some tracks might not have features
                    track['features'] = feature
            
            return tracks
            
        except Exception as e:
            logger.error(f"Failed to get recent tracks: {str(e)}")
            raise
    
    async def get_top_tracks(
        self,
        time_range: str = "short_term",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's top tracks.
        
        Args:
            time_range: Time range for top tracks (short_term, medium_term, long_term)
            limit: Maximum number of tracks to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of top tracks with audio features
            
        Raises:
            HTTPException: If track retrieval fails
        """
        try:
            # Get top tracks
            top_tracks = self.client.current_user_top_tracks(
                limit=limit,
                offset=0,
                time_range=time_range
            )
            
            if not top_tracks or not top_tracks['items']:
                return []
            
            # Get audio features for all tracks
            track_ids = [track['id'] for track in top_tracks['items']]
            audio_features = self.client.audio_features(track_ids)
            
            # Combine track data with audio features
            tracks_data = []
            for track, features in zip(top_tracks['items'], audio_features):
                if not features:
                    continue
                    
                tracks_data.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'features': AudioFeatures(
                        valence=features['valence'],
                        energy=features['energy'],
                        danceability=features['danceability'],
                        instrumentalness=features['instrumentalness'],
                        tempo=features['tempo'],
                        mode=features['mode']
                    )
                })
            
            return tracks_data
            
        except Exception as e:
            logger.error(f"Failed to get top tracks: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get top tracks from Spotify"
            )
