import uuid

from pydantic import UUID4
from typing import List

from models.workspace import Workspace
from schemas.workspace import WorkspaceCreate, WorkspaceInDB
from exceptions.core import CoreException
from services.base import CRUDBase


class WorkspaceService(CRUDBase):
    async def list_all(self) -> List[WorkspaceInDB]:
        workspaces = self._query(Workspace).order_by(Workspace.id).all()
        return workspaces

    async def list_by_id(self, workspace_id: UUID4) -> WorkspaceInDB:
        result = self._query(Workspace).filter(Workspace.id == workspace_id).first()
        if result is None:
            raise (
                CoreException.NotFound(
                    message=f"Not found workspace with id {workspace_id}"
                )
            )
        return result

    async def create(self, workspace: WorkspaceCreate) -> WorkspaceInDB:
        result = self._query(Workspace).filter(Workspace.name == workspace.name).first()
        if result is not None:
            raise (CoreException.UniqueViolationError())

        workspace_obj = Workspace(name=workspace.name, provider=workspace.provider)
        return self._create(workspace_obj)
