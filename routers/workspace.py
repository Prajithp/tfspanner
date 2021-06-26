from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from typing import List, Union, Any
from sqlalchemy.orm import Session
from pydantic import UUID4

from config.database import db_obj as _db

import schema.workspace as Schema
import service.workspace as Service

router = APIRouter(
    prefix="/workspace",
    tags=["projects"],
    responses={404: {"message": "Not found"}},
)

@router.get("/", response_model=List[Schema.Workspace])
async def list_workspaces(db: Session = Depends(_db)) -> List[Schema.Workspace]:
    if result := Service.Workspace(db).list():
        return result

    return JSONResponse(status_code=404, content={"message": "Nothing found"})

@router.get("/{workspace_id}", response_model=Schema.Workspace)
async def get_workspace(workspace_id: UUID4, db: Session = Depends(_db)):
    if result := Service.Workspace(db).list(workspace_id):
        return result
    return JSONResponse(status_code=404, content={"message": "Nothing found"})

@router.post("/", response_model=Schema.Workspace)
async def create_project(project: Schema.WorkspaceIn,  db: Session = Depends(_db)):
    if result := Service.Workspace(db).create(project):
        return result
    return JSONResponse(status_code=404, content={"message": "Nothing found"})
