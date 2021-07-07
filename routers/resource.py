from aioredis import Redis, Channel
from aioredis.errors import ConnectionClosedError
from fastapi import APIRouter, Depends, status, WebSocket
from fastapi.responses import JSONResponse
from typing import List, Optional, Union, Any
from sqlalchemy.orm import Session, session
from pydantic import UUID4
from starlette.websockets import WebSocketDisconnect

from config.database import db_session
from fastapi_plugins import depends_redis
from schemas.resource import (
    ResourceCreate,
    ResourceInDB,
    ResourceState,
    TfTaskAction,
    TfTaskActionBody,
    TfTaskInfo,
)
from services.resource import ResourceService
from utils.logger import getLogger

logger = getLogger(__name__)

router = APIRouter(
    prefix="/resources",
    tags=["resource"],
    responses={404: {"message": "Not found"}},
)

@router.get("/workspace/{workspace_id}", response_model=List[ResourceInDB])
async def get_all_resources(
    workspace_id: UUID4, db: Session = Depends(db_session)
) -> List[ResourceInDB]:
    return await ResourceService(db).list_all(workspace_id)


@router.post("/workspace/{workspace_id}", response_model=ResourceInDB)
async def create_resource(
    workspace_id: UUID4, resource: ResourceCreate, db: Session = Depends(db_session)
) -> List[ResourceInDB]:
    return await ResourceService(db).create(workspace_id, resource)


@router.put(
    "/{resource_id}/task/{action}",
    response_model=TfTaskInfo,
    status_code=status.HTTP_201_CREATED,
)
async def start_task(
    resource_id: UUID4,
    action: TfTaskAction,
    parameter: Optional[TfTaskActionBody],
    db: Session = Depends(db_session),
):
    return await ResourceService(db).start_task(resource_id, action, parameter)


@router.websocket("/{resource_id}/task/stream/")
async def stream_tf_result(websocket: WebSocket, resource_id: UUID4, redis: Redis = Depends(depends_redis)):
    await websocket.accept()
    (channel,) = await redis.subscribe(channel=Channel(str(resource_id), False))
    try:
        while True:
            message = await channel.get(encoding='utf-8')
            if message:
                await websocket.send_json({"message": message})
    except Exception as e:
        await websocket.close()