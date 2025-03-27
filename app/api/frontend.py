"""Frontend routes for the application."""

import logging
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.spotify import SpotifyService
from app.services.mood_analyzer import MoodAnalyzer
from app.core.auth import create_spotify_oauth
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page."""
    try:
        # Check if user is logged in
        access_token = request.session.get("access_token")
        if not access_token:
            logger.info("User not logged in, showing login page")
            return templates.TemplateResponse(
                "login.html",
                {"request": request}
            )

        # User is logged in, show dashboard
        logger.info("User logged in, redirecting to dashboard")
        return await dashboard(request)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "An unexpected error occurred"
            }
        )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the dashboard page."""
    try:
        # Check if user is logged in
        access_token = request.session.get("access_token")
        if not access_token:
            logger.info("User not logged in, redirecting to login")
            return templates.TemplateResponse(
                "login.html",
                {"request": request}
            )

        # Initialize services
        spotify = SpotifyService(access_token)
        mood_analyzer = MoodAnalyzer()

        # Get user's recent tracks
        recent_tracks = await spotify.get_recently_played_tracks()
        if not recent_tracks:
            logger.warning("No recent tracks found")
            recent_tracks = []

        # Analyze mood
        current_mood = mood_analyzer.analyze_current_mood(recent_tracks)
        trend_data = mood_analyzer.analyze_mood_trend(recent_tracks)
        recommendations = mood_analyzer.get_recommendations(current_mood)

        logger.info(f"Generated mood analysis: {current_mood['primary_mood']}")
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "current_mood": current_mood,
                "recent_tracks": recent_tracks,
                "trend_data": trend_data,
                "recommendations": recommendations
            }
        )
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "An error occurred while loading your dashboard"
            }
        )
