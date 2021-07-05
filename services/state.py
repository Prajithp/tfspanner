from os import stat
import uuid, json
from sqlalchemy.orm import Session
from pydantic import UUID4
from typing import List
from models.state import Lock, State
from schemas.state import StateLockCreate, StateLockInDB, TfState, StateInDB, TfResource
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

    async def is_locked(self, workspace_id: UUID4) -> StateLockInDB:
        lock = self._query(Lock).filter(Lock.workspace_id == workspace_id).first()
        return lock

    async def lock_state(
        self, workspace_id: UUID4, info: StateLockCreate
    ) -> StateLockInDB:
        lock = await self.is_locked(workspace_id)
        if lock is not None:
            raise (CoreException.ResourceLocked(lock.id))

        lock_obj = Lock(workspace_id=workspace_id, **info.dict())
        self._create(lock_obj)
        return lock_obj

    async def unlock_state(
        self, workspace_id: UUID4, lock_info: StateLockCreate
    ) -> StateLockInDB:
        lock = await self.is_locked(workspace_id)

        if lock is None:
            raise (
                CoreException.NotFound(
                    f"Could not find any lock for workspace {workspace_id}"
                )
            )

        if lock.id != lock_info.id:
            raise (CoreException.ResourceLockConflict(lock_info.id))

        try:
            self.db.delete(lock)
            self.db.commit()
        except Exception as e:
            raise (e)

        return lock
