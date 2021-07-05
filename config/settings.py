from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl, RedisDsn
from pydantic.types import DirectoryPath


class Settings(BaseSettings):
    BASE_DIR: DirectoryPath = Path(__file__).parent.parent
    BASE_URL: AnyHttpUrl = "http://localhost:8000"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "test"
    POSTGRES_DB: str = "terraspanner"

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_SERVER: str = "localhost"
    REDIS_PORT: str = "6379"
    CELERY_ONCE_REDIS_URI: str = f"redis://{REDIS_SERVER}:{REDIS_PORT}/0"
    AIOREDIS_URI: Optional[RedisDsn] = None

    @validator("AIOREDIS_URI", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_SERVER"),
            port=values.get("REDIS_PORT"),
            path="/0",
        )

    class Config:
        case_sensitive = True


settings = Settings()
