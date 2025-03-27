"""API routes for mood analysis."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from app.schemas.mood import MoodAnalysis
from app.services.mood_analyzer import MoodAnalyzer
from app.core.config import settings

router = APIRouter()
mood_analyzer = MoodAnalyzer(debug=True)  # TODO: Use settings.DEBUG

@router.get("/recent", response_model=MoodAnalysis)
async def analyze_recent_mood(
    request: Request,
    limit: Optional[int] = 50
) -> MoodAnalysis:
    """Analyze mood from recent tracks.
    
    Args:
        request: FastAPI request object
        limit: Maximum number of tracks to analyze
        
    Returns:
        MoodAnalysis: Analysis results including mood scores and trends
        
    Raises:
        HTTPException: If mood analysis fails
    """
    try:
        return await mood_analyzer.analyze_debug_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze mood: {str(e)}"
        )
