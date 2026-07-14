"""
Centralized configuration, loaded from environment variables / .env file.
Import `settings` anywhere you need credentials instead of hardcoding them.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            f"Add it to your .env file (see .env.example)."
        )
    return value


@dataclass(frozen=True)
class Settings:
    google_api_key: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    llm_model: str = "gemini-1.5-flash"
    chunk_size: int = 1000
    chunk_overlap: int = 200


def load_settings() -> Settings:
    return Settings(
        google_api_key=_require("GOOGLE_API_KEY"),
        neo4j_uri=_require("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=_require("NEO4J_USER", "neo4j"),
        neo4j_password=_require("NEO4J_PASSWORD"),
        llm_model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
    )


# Lazily built on first import; callers that just need types don't pay the cost.
settings: Settings | None = None
try:
    settings = load_settings()
except RuntimeError:
    # Allow importing this module (e.g. for tests) without a configured .env.
    # Anything that actually calls the LLM/DB will raise clearly when it tries.
    pass
