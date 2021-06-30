from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List, Union, Any
from sqlalchemy.orm import Session
from pydantic import UUID4

from config.database import db_session
from schemas.state import TfState, TfResource
from services.state import StateService

router = APIRouter(
    prefix="/states",
    tags=["state"],
    responses={404: {"message": "Not found"}},
)


@router.get("/resources/workspace/{workspace_id}/", response_model=List[TfResource])
async def get_resources(
    workspace_id: UUID4, db: Session = Depends(db_session)
) -> List[TfResource]:
    return await StateService(db).list_resources(workspace_id)


@router.get("/remote/workspace/{workspace_id}/", response_model=TfState)
async def get_state(workspace_id: UUID4, db: Session = Depends(db_session)) -> TfState:
    return await StateService(db).list_by_workspace_id(workspace_id)


@router.post("/remote/workspace/{workspace_id}/", response_model=TfState)
async def create_state(
    workspace_id: UUID4, state: TfState, db: Session = Depends(db_session)
) -> TfState:
    return await StateService(db).create_or_update(workspace_id, state)
