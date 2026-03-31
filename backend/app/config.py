"""Application configuration via environment variables."""
import os
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # API
    anthropic_api_key: str = ""
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Database
    database_url: str = "sqlite+aiosqlite:///./harness.db"

    # CORS
    cors_origins: str = "*"

    # Paths — works both local and deployed
    project_root: Path = Path(__file__).parent.parent.parent
    harnesses_dir: Path = project_root / "harnesses"
    domains_dir: Path = project_root / "domains"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
