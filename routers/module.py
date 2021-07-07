from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from config.database import db_session
from schemas.module import ModuleCreate, ModuleInDB, ModuleOut
from services.module import ModuleService

router = APIRouter(
    prefix="/modules",
    tags=["modules"],
    responses={404: {"message": "Not found"}},
)


@router.get("/", response_model=List[ModuleOut])
async def get_all_modules(db: Session = Depends(db_session)) -> List[ModuleInDB]:
    return await ModuleService(db).get_all()


@router.post("/", response_model=ModuleOut)
async def create_module(module: ModuleCreate, db: Session = Depends(db_session)):
    return await ModuleService(db).add_module(module)


@router.get("/{module_id}/", response_model=ModuleOut)
async def get_module(module_id: UUID, db: Session = Depends(db_session)):
    return await ModuleService(db).get_by_id(module_id)


@router.get("/{module_id}/reindex/", response_model=ModuleOut)
async def reindex_module(module_id: UUID, db: Session = Depends(db_session)):
    return await ModuleService(db).reindex_module(module_id)


@router.get("/{module_id}/variables/", response_model=Dict[Any, Any])
async def get_variables(module_id: UUID, db: Session = Depends(db_session)):
    return await ModuleService(db).get_variables_by_id(module_id)


@router.get("/{module_id}/outputs/", response_model=Dict[Any, Any])
async def get_outputs(module_id: UUID, db: Session = Depends(db_session)):
    return await ModuleService(db).get_outputs_by_id(module_id)
