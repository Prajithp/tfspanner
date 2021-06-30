from os import stat
import uuid, json
from sqlalchemy.orm import Session
from pydantic import UUID4
from typing import List

from models.state import State
from schemas.state import TfState, StateInDB, TfResource
from exceptions.core import CoreException
from services.base import CRUDBase


class StateService(CRUDBase):
    async def create_or_update(
        self, workspace_id: UUID4, tfstate: TfState
    ) -> StateInDB:
        state_obj = (
            self._query(State).filter(State.workspace_id == workspace_id).first()
        )
        if state_obj is not None:
            self._update(state_obj, state=tfstate.dict())
            return state_obj.state

        state_obj = State(workspace_id=workspace_id, state=tfstate.dict())
        self._create(state_obj)
        return state_obj.state

    async def list_by_workspace_id(self, workspace_id: UUID4):
        result = self._query(State).filter(State.workspace_id == workspace_id).first()
        if not result:
            raise (
                CoreException.NotFound(
                    message=f"Not found state  with id {workspace_id}"
                )
            )

        return result.state

    async def list_resources(self, workspace_id: UUID4) -> List[TfResource]:
        result = self._query(State).filter(State.workspace_id == workspace_id).first()
        if not result:
            raise (
                CoreException.NotFound(
                    message=f"Not found state  with id {workspace_id}"
                )
            )

        resources = []
        for resource in result.state["resources"]:
            module = resource["module"] if resource.get("module") else "none"
            resource_obj = TfResource(
                module=module,
                type=resource["type"],
                name=resource["name"],
                dependencies=resource.get("dependencies", []),
            )
            resources.append(resource_obj)

        return resources
