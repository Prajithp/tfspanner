import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import UUID4

from models.workspace import Workspace as WorkspaceModel
from schema.workspace import WorkspaceIn
from exceptions.core import CoreException
from service.base import CRUDBase

class Workspace(CRUDBase):
    async def list_all(self):
        workspaces = self.db.query(WorkspaceModel).order_by(WorkspaceModel.id).all()
        return workspaces

    async def list_by_id(self, workspace_id: Optional[UUID4]):
        result = self._db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
        if result is None:
            raise(CoreException.NotFound(message = f"Not found workspace with id {workspace_id}"))
        return result
    
    async def create(self, workspace: WorkspaceIn):
        result = self._query(WorkspaceModel).filter(WorkspaceModel.name == workspace.name).first()
        if result is not None:
            raise(CoreException.UniqueViolationError())

        workspace_obj = WorkspaceModel(name = workspace.name, provider = workspace.provider)
        workspace     = self._create(workspace_obj)
        return workspace

    