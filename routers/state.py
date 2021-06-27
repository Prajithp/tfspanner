from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from typing import List, Union, Any
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import UUID4

from config.database import db_session

import schema.state  as Schema
import service.state as Service

router = APIRouter(
    prefix="/states",
    tags=["state"],
    responses={404: {"message": "Not found"}},
)

@router.get("/remote/workspace/{workspace_id}/", response_model=Schema.TerraState)
async def get_state(workspace_id: UUID4, db: AsyncSession = Depends(db_session)) -> Schema.TerraState:
    return await Service.State(db).list_by_workspace_id(workspace_id)

@router.post("/remote/workspace/{workspace_id}/", response_model=Schema.TerraState)
async def create_state(workspace_id: UUID4, state: Schema.TerraState, db: AsyncSession = Depends(db_session)) -> Schema.TerraState:
    return await Service.State(db).create_or_update(workspace_id, state)

