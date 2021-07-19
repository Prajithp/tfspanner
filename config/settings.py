from ipaddress import IPv4Address
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl, RedisDsn
from pydantic.types import DirectoryPath
from fastapi_plugins import RedisSettings
import yaml


class Settings(RedisSettings, BaseSettings):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5000

    BASE_DIR: DirectoryPath = Path(__file__).parent.parent
    URL_PREFIX: str = "/tfspanner/v1"
    OPENAPI_URL: str = URL_PREFIX + "/openapi.json"
    OPENAPI_DOC_URL: str = URL_PREFIX + "/doc"
    OPENAPI_REDOC_URL: str = URL_PREFIX + "/redoc"
    BASE_URL: AnyHttpUrl = "http://localhost:8000" + URL_PREFIX

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

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    CELERY_REDIS_URI: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


app_env = os.environ.get("APPLICATION_ENV", "development").lower()
config_file = Path(__file__).parent.joinpath("settings", f"{app_env}.yml")

with open(config_file, "r") as fh:
    config = yaml.load(fh, Loader=yaml.FullLoader)

settings = Settings(**config)
