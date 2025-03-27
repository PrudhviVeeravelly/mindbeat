"""Pydantic schemas for mood analysis."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AudioFeatures(BaseModel):
    """Audio features from a track.
    
    These features are obtained from Spotify's audio analysis and are used
    to compute the mood score of a track.
    """
    
    valence: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    danceability: float = Field(..., ge=0.0, le=1.0)
    instrumentalness: float = Field(..., ge=0.0, le=1.0)
    tempo: float = Field(..., ge=0.0)
    mode: int = Field(..., ge=0, le=1)

class TrackMood(BaseModel):
    """Mood analysis for a single track.
    
    Contains the computed mood score and relevant audio features that
    contributed to the mood analysis.
    """
    
    mood_score: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=0.0, le=1.0)

class MoodAnalysis(BaseModel):
    """Complete mood analysis results.
    
    Contains overall mood analysis results, including the average mood score,
    energy levels, trends over time, and analyzed tracks.
    """
    
    overall_mood: float = Field(..., ge=0.0, le=1.0)
    average_energy: float = Field(..., ge=0.0, le=1.0)
    mood_trend: List[float] = Field(..., min_items=1)
    tracks: List[TrackMood]

class MoodRecommendation(BaseModel):
    """Personalized mood-based recommendation."""
    
    title: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
