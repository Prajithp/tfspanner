from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List, Union, Any
from sqlalchemy.orm import Session
from pydantic import UUID4

from config.database import db_session
from schemas.resource import ResourceInDB
from services.resource import ResourceService

router = APIRouter(
    prefix="/resources",
    tags=["modules"],
    responses={404: {"message": "Not found"}},
)


@router.get("/", response_model=List[ResourceInDB])
async def get_all_resources(db: Session = Depends(db_session)) -> List[ResourceInDB]:
    return await ResourceService(db).list_all()
