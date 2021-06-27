import uuid, json
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError

from pydantic import UUID4
from models.state import States as StatesModel
from schema.state import TerraState, State

from exceptions.core import CoreException

class State(object):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_update(self, workspace_id: UUID4, state: TerraState) -> State:
        result = await self.db.execute(select(StatesModel).filter(StatesModel.workspace_id == workspace_id))
        result = result.scalar()
        if result is not None:
            state_obj = result
            state_obj.state = state.dict()
            await self.db.commit()
            await self.db.refresh(state_obj)
            return state_obj.state

        state_obj = StatesModel(workspace_id = workspace_id, state = state.dict())
        self.db.add(state_obj)
        await self.db.commit()
        await self.db.refresh(state_obj)

        return state_obj.state

    async def list_by_workspace_id(self, workspace_id: UUID4):
        result = await self.db.execute(select(StatesModel.state).filter(StatesModel.workspace_id == workspace_id))
        if not result:
            raise(CoreException.NotFound(message = f"Not found state  with id {workspace_id}"))

        return result.scalar()
