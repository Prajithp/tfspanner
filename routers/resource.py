from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List, Union, Any
from sqlalchemy.orm import Session
from pydantic import UUID4

from config.database import db_session
from schemas.resource import ResourceCreate, ResourceInDB
from services.resource import ResourceService

router = APIRouter(
    prefix="/resources",
    tags=["resource"],
    responses={404: {"message": "Not found"}},
)


@router.get("/workspace/{workspace_id}/", response_model=List[ResourceInDB])
async def get_all_resources(
    workspace_id: UUID4, db: Session = Depends(db_session)
) -> List[ResourceInDB]:
    return await ResourceService(db).list_all(workspace_id)


@router.post("/workspace/{workspace_id}/", response_model=ResourceInDB)
async def create_resource(
    workspace_id: UUID4, resource: ResourceCreate, db: Session = Depends(db_session)
) -> List[ResourceInDB]:
    return await ResourceService(db).create(workspace_id, resource)
