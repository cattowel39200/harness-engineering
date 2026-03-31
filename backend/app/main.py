"""Harness Engineering Platform - FastAPI Application."""
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.models.base import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Harness Engineering Platform",
    description="AI Agent Harness Framework - constraints and guidelines for safe, high-quality AI outputs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Harness Engineering Platform",
        "version": "0.1.0",
        "status": "running",
    }
