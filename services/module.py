import json
from typing import Any, Dict, Optional
from fastapi import exceptions
from pydantic import UUID4
from tasks.module import build_module_meta_data
from models.module import Module
from schemas.module import ModuleCreate, ModuleInDB, ModuleOut, ModuleState
from exceptions.core import CoreException
from services.base import CRUDBase
from celery_singleton.exceptions import DuplicateTaskError


class ModuleService(CRUDBase):
    async def get_all(self) -> ModuleOut:
        modules = (
            self.db.query(Module.id, Module.name, Module.source, Module.state)
            .order_by(Module.id)
            .all()
        )

        return modules

    async def add_module(self, module: ModuleCreate) -> ModuleOut:
        result = self._query(Module).filter(Module.name == module.name).first()
        if result is not None:
            raise (CoreException.UniqueViolationError())

        module_obj = Module(name=module.name, source=module.source)
        module_obj = self._create(module_obj)
        """
        UUID object is not converting to proper string when using dict()
        so this is an hacky way to convert all object in to proper string
        """
        module_schema = json.loads(ModuleInDB.from_orm(module_obj).json())

        custom_task_id = str(module_obj.id)
        try:
            task_id = build_module_meta_data.apply_async(
                args=[module_schema], task_id=custom_task_id
            )
        except DuplicateTaskError as e:
            raise (CoreException.DuplicateTaskError(e.task_id))

        return module_obj

    async def reindex_module(self, module_id: UUID4) -> ModuleOut:
        module = await self.get_by_id(module_id)

        self._update(module, state=ModuleState.PENDING)

        module_schema = json.loads(ModuleInDB.from_orm(module).json())

        custom_task_id = str(module.id)
        try:
            task_id = build_module_meta_data.apply_async(
                args=[module_schema], task_id=custom_task_id
            )
        except DuplicateTaskError as e:
            raise (CoreException.DuplicateTaskError(e.task_id))

        return module

    async def get_by_id(self, module_id: UUID4) -> ModuleOut:
        result = self._query(Module).filter(Module.id == module_id).first()
        if result is None:
            raise (CoreException.NotFound(message=f"Not found any modules"))

        return result

    async def get_variables_by_id(self, module_id: UUID4) -> Dict[Any, Any]:
        result = await self.get_by_id(module_id)
        return result.variables

    async def get_outputs_by_id(self, module_id: UUID4) -> Dict[Any, Any]:
        result = await self.get_by_id(module_id)
        return result.outputs
