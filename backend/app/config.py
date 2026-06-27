"""Application configuration, loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Async SQLAlchemy URL. The docker-compose db service is reachable as "db".
    database_url: str = "postgresql+asyncpg://hyogen:hyogen@db:5432/hyogen"

    # kanjiapi.dev base. Per-character data lives at {base}/kanji/{char}.
    kanjiapi_base: str = "https://kanjiapi.dev/v1"

    # Seconds to wait on any single outbound HTTP call (kanjiapi / YT Music).
    http_timeout: float = 15.0

    # Comma-separated list of allowed CORS origins for the browser frontend.
    cors_origins: str = "http://localhost,https://localhost,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
