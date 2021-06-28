from os import stat
import uuid, json
from sqlalchemy.orm import Session
from pydantic import UUID4

from models.state import States as StatesModel
from schema.state import TerraState, State
from exceptions.core import CoreException
from service.base import CRUDBase

class State(CRUDBase):
    async def create_or_update(self, workspace_id: UUID4, terra_state: TerraState) -> State:
        state_obj = self._query(StatesModel).filter(StatesModel.workspace_id == workspace_id).first()
        if state_obj is not None:
            self._update(state_obj, state = terra_state.dict())
            return state_obj.state

        state_obj = StatesModel(workspace_id = workspace_id, state = terra_state.dict())
        self._create(state_obj)
        return state_obj.state

    async def list_by_workspace_id(self, workspace_id: UUID4):
        result = self._query(StatesModel).filter(StatesModel.workspace_id == workspace_id).first()
        if not result:
            raise(CoreException.NotFound(message = f"Not found state  with id {workspace_id}"))

        return result.state
