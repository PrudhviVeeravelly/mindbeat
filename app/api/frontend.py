"""Frontend routes for the application."""

from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.spotify import SpotifyService
from app.services.mood_analyzer import MoodAnalyzer
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory="app/frontend/templates")
mood_analyzer = MoodAnalyzer()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the dashboard page."""
    try:
        # Get token info from session
        token_info = request.session.get("token_info")
        if not token_info:
            # Not logged in, show login page
            return templates.TemplateResponse(
                "login.html",
                {"request": request}
            )

        # Initialize services with access token
        spotify = SpotifyService(token_info['access_token'])

        # Get user profile and recent tracks
        user = await spotify.get_user_profile()
        recent_tracks = await spotify.get_recent_tracks(limit=20)

        # Calculate mood scores
        current_mood = mood_analyzer.analyze_current_mood(recent_tracks)
        trend_data = mood_analyzer.analyze_mood_trend(recent_tracks)

        # Generate recommendations
        recommendations = mood_analyzer.get_recommendations(current_mood)

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "current_mood": current_mood,
                "recent_tracks": recent_tracks,
                "trend_dates": trend_data["dates"],
                "trend_scores": trend_data["scores"],
                "recommendations": recommendations
            }
        )

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Failed to load dashboard. Please try logging in again."
            }
        )
