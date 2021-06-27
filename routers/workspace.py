from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from typing import List, Union, Any
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import UUID4

from config.database import db_session

import schema.workspace as Schema
import service.workspace as Service

router = APIRouter(
    prefix="/workspace",
    tags=["projects"],
    responses={404: {"message": "Not found"}},
)

@router.get("/", response_model=List[Schema.Workspace])
async def list_workspaces(db: AsyncSession = Depends(db_session)) -> List[Schema.Workspace]:
    if result := await Service.Workspace(db).list_all():
        return result

@router.get("/{workspace_id}", response_model=Schema.Workspace)
async def get_workspace(workspace_id: UUID4, db: AsyncSession = Depends(db_session)):
    if result := await Service.Workspace(db).list_by_id(workspace_id):
        return result

@router.post("/", response_model=Schema.Workspace)
async def create_project(project: Schema.WorkspaceIn,  db: AsyncSession = Depends(db_session)):
    if result := await Service.Workspace(db).create(project):
        return result
