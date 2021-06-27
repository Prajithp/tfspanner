import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError

from pydantic import UUID4
from models.workspace import Workspace as WorkspaceModel
from schema.workspace import WorkspaceIn

from exceptions.core import CoreException

class Workspace(object):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_all(self):
        stmt       = select(WorkspaceModel).order_by(WorkspaceModel.id)
        result     = await self.db.execute(stmt)
        workspaces = result.scalars().all()
        
        return workspaces

    async def list_by_id(self, workspace_id: Optional[UUID4]):
        result = await self.db.execute(select(WorkspaceModel).filter(WorkspaceModel.id == workspace_id))
        workspace = result.scalars().one_or_none()
        if workspace is None:
            raise(CoreException.NotFound(message = f"Not found workspace with id {workspace_id}"))
        return workspace
    
    async def create(self, workspace: WorkspaceIn):
        result = await self.db.execute(select(WorkspaceModel).filter(WorkspaceModel.name == workspace.name))
        result = result.scalar()
        if result is not None:
            raise(CoreException.UniqueViolationError())

        workspace = WorkspaceModel(name = workspace.name, provider = workspace.provider)
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)

        return workspace
