"""Harness management endpoints."""
from fastapi import APIRouter, HTTPException
from app.core.harness_loader import harness_loader

router = APIRouter()


@router.get("")
async def list_harnesses():
    """List all available harness definitions."""
    return harness_loader.list_harnesses()


@router.get("/{slug}")
async def get_harness(slug: str):
    """Get a parsed harness definition."""
    try:
        h = harness_loader.load(slug)
        return h.model_dump()
    except FileNotFoundError:
        raise HTTPException(404, f"Harness not found: {slug}")
