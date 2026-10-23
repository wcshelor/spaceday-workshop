from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings


def _repo_root() -> Path:
    candidate = Path(__file__).resolve().parents[2]
    # Validate candidate looks like the project root (contains backend + frontend markers).
    # This resolves correctly in both the local checkout and /app in the container.
    if (candidate / "backend" / "app" / "main.py").exists() or (candidate / "frontend" / "package.json").exists():
        return candidate
    # Search upward for a directory containing repo markers
    for parent in Path(__file__).resolve().parents:
        if (parent / "backend" / "app" / "main.py").exists() or (parent / "frontend" / "package.json").exists():
            return parent
    # Container fallback
    if Path("/app").exists() and (Path("/app") / "backend").exists():
        return Path("/app")
    return candidate


class Settings(BaseSettings):
    # Paths relative to repo root unless absolute
    data_dir: Path = _repo_root() / "data" / "workshop"
    artifacts_dir: Path = _repo_root() / "artifacts"
    scoring_artifact: Path = _repo_root() / "artifacts" / "scoring-v1"
    language_artifact: Path = _repo_root() / "artifacts" / "language-v1"

    # Language / encoder
    language_mode: str = "disabled"  # disabled | prepared | live
    encoder_endpoint: str | None = None
    encoder_model_id: str = "laion/clap-htsat-unfused"
    text_encoder_timeout_seconds: float = 15.0
    text_cache_size: int = 256
    text_concurrency: int = 4
    text_queue_size: int = 20

    # API
    cors_allow_origins: str = "http://localhost:5173,http://localhost:3000"
    request_deadline_seconds: float = 15.0

    # Scoring
    scoring_config: Path = _repo_root() / "config" / "scoring-v1.json"

    class Config:
        env_file = ".env"
        env_prefix = "SPACEDAY_"


settings = Settings()

# Resolve relative paths against repo root if they came from env as relative
def resolve_settings(s: Settings) -> Settings:
    root = _repo_root()
    for field in ["data_dir", "artifacts_dir", "scoring_artifact", "language_artifact", "scoring_config"]:
        p = getattr(s, field)
        if isinstance(p, Path) and not p.is_absolute():
            setattr(s, field, (root / p).resolve())
    return s

settings = resolve_settings(settings)
