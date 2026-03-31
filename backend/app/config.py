"""Application configuration via environment variables."""
import os
from pydantic_settings import BaseSettings
from pathlib import Path


# Detect if running in deployed environment
_backend_dir = Path(__file__).parent.parent  # backend/
_project_root = _backend_dir.parent          # harness-engineering/

# On Render, rootDir=backend, so harnesses/domains are one level up
# But they might not exist if rootDir only has backend/
# Copy them into backend/ at build time, or reference from project root
if (_project_root / "harnesses").exists():
    _harnesses = _project_root / "harnesses"
    _domains = _project_root / "domains"
elif (_backend_dir / "harnesses").exists():
    _harnesses = _backend_dir / "harnesses"
    _domains = _backend_dir / "domains"
else:
    _harnesses = _project_root / "harnesses"
    _domains = _project_root / "domains"


class Settings(BaseSettings):
    # API
    anthropic_api_key: str = ""
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Database
    database_url: str = "sqlite+aiosqlite:///./harness.db"

    # CORS
    cors_origins: str = "*"

    # Paths
    project_root: Path = _project_root
    harnesses_dir: Path = _harnesses
    domains_dir: Path = _domains

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
