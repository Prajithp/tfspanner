from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from config.database import db_session
from schemas.module import ModuleCreate, ModuleInDB
from services.module import ModuleService

router = APIRouter(
    prefix="/modules",
    tags=["modules"],
    responses={404: {"message": "Not found"}},
)


@router.get("/", response_model=List[ModuleInDB])
async def get_all_modules(db: Session = Depends(db_session)) -> List[ModuleInDB]:
    return await ModuleService(db).list_all()

@router.post("/", response_model=ModuleInDB)
async def create_module(module: ModuleCreate, db: Session = Depends(db_session)):
    return await ModuleService(db).add_module(module)