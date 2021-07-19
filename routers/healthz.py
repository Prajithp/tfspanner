from typing import Dict
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import Response
from config.database import db_session
from aioredis import Redis
from pydantic import BaseModel
from fastapi_plugins import depends_redis


class Liveness(BaseModel):
    status: str = "OK"


class Readiness(Liveness):
    database: str
    redis: str


router = APIRouter(
    prefix="/healthz",
    tags=["healthz"],
    responses={404: {"message": "Not found"}},
)


@router.get("/liveness", response_model=Liveness)
async def liveness_check() -> Liveness:
    return dict(status="OK")


@router.get("/readiness", response_model=Readiness)
async def readiness_check(
    response: Response,
    db: Session = Depends(db_session),
    redis: Redis = Depends(depends_redis),
):
    check = {"status": "OK", "database": "OK", "redis": "OK"}
    try:
        r = db.execute("SELECT 1").fetchone()
    except Exception as e:
        check["database"] = str(e)
        check["status"] = "ERROR"

    try:
        ping = await redis.ping()
        check["redis"] = ping
    except Exception as e:
        check["redis"] = str(e)
        check["status"] = "ERROR"

    if check["status"] == "ERROR":
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return check
