"""API router aggregation."""
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.harnesses import router as harnesses_router
from app.api.domains import router as domains_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(harnesses_router, prefix="/harnesses", tags=["harnesses"])
api_router.include_router(domains_router, prefix="/domains", tags=["domains"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
