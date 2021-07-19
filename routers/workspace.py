from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List, Union, Any
from sqlalchemy.orm import Session
from pydantic import UUID4

from config.database import db_session
from schemas.workspace import WorkspaceCreate, WorkspaceInDB
from services.workspace import WorkspaceService

router = APIRouter(
    prefix="/workspaces",
    tags=["workspace"],
    responses={404: {"message": "Not found"}},
)


@router.get("", response_model=List[WorkspaceInDB])
async def list_workspaces(db: Session = Depends(db_session)) -> List[WorkspaceInDB]:
    return await WorkspaceService(db).list_all()


@router.get("/{workspace_id}", response_model=WorkspaceInDB)
async def get_workspace(
    workspace_id: UUID4, db: Session = Depends(db_session)
) -> WorkspaceInDB:
    return await WorkspaceService(db).list_by_id(workspace_id)


@router.post("", response_model=WorkspaceInDB)
async def create_workspace(
    workspace: WorkspaceCreate, db: Session = Depends(db_session)
):
    return await WorkspaceService(db).create(workspace)
