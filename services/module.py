import uuid
from typing import Optional
from pydantic import UUID4

from models.module import Module
from schemas.module import ModuleCreate

from exceptions.core import CoreException
from services.base import CRUDBase


class ModuleService(CRUDBase):
    async def get_all(self):
        modules = self.db.query(Module).order_by(Module.id).all()
        if modules is None:
            raise (
                CoreException.NotFound(
                    message=f"Not found workspace with id {workspace_id}"
                )
            )

        return modules

    async def add_module(self, module: ModuleCreate):
        result = self._query(Module).filter(Workspace.name == workspace.name).first()
        if result is not None:
            raise (CoreException.UniqueViolationError())

        workspace_obj = Workspace(name=workspace.name, provider=workspace.provider)
        return self._create(workspace_obj)