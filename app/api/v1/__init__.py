"""API v1 router."""

from fastapi import APIRouter
from app.api.v1 import mood

api_router = APIRouter()
api_router.include_router(mood.router, prefix="/mood", tags=["mood"])
