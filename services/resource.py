from sys import stderr
from typing import List, Optional
from celery.app import task
from sqlalchemy.sql.elements import and_
from starlette import status
from schemas.resource import (
    ResourceCreate,
    ResourceInDB,
    ResourceState,
    TfTaskAction,
    TfTaskActionBody,
    TfTaskInfo,
)
from pydantic.types import UUID4
from models.resource import Resource
from exceptions.core import CoreException, CoreExceptionBase
from services.base import CRUDBase
from tasks.tfrunner import tf_apply, tf_plan
from celery_singleton.exceptions import DuplicateTaskError


class TfTaskConflict(CoreExceptionBase):
    def __init__(self, message: str) -> None:
        status_code = status.HTTP_409_CONFLICT
        CoreExceptionBase.__init__(self, status_code, message)


class ResourceService(CRUDBase):
    async def list_all(self, workspace_id: UUID4) -> List[ResourceInDB]:
        resources = (
            self.db.query(Resource)
            .filter(Resource.workspace_id == workspace_id)
            .order_by(Resource.updated_at)
            .all()
        )

        return resources

    async def resource_by_name_and_workspace(
        self, workspace_id: UUID4, resource_name: str
    ) -> ResourceInDB:
        return (
            self._query(Resource)
            .filter(
                and_(
                    Resource.workspace_id == workspace_id,
                    Resource.name == resource_name,
                )
            )
            .first()
        )

    async def create(
        self, workspace_id: UUID4, resource_info: ResourceCreate
    ) -> ResourceInDB:
        is_exists = await self.resource_by_name_and_workspace(
            workspace_id, resource_info.name
        )
        if is_exists is not None:
            raise (
                CoreException.UniqueViolationError(
                    "Resource with same name is already exists"
                )
            )

        resource = Resource(workspace_id=workspace_id, **resource_info.dict())
        self._create(resource)

        return resource

    async def start_task(
        self,
        resource_id: UUID4,
        action: TfTaskAction,
        param: Optional[TfTaskActionBody],
    ) -> TfTaskInfo:
        resource = self._query(Resource).filter(Resource.id == resource_id).first()
        if resource is None:
            raise (CoreException.NotFound(f"Not found resource with id {resource_id}"))

        resource_id = str(resource_id)
        if action == TfTaskAction.plan:
            try:
                task_id = tf_plan.apply_async(
                    args=[resource_id, param.dict()], task_id=resource_id
                )
            except DuplicateTaskError as e:
                raise (CoreException.DuplicateTaskError(e.task_id))
            return dict(task_id=str(task_id))
        elif action == TfTaskAction.apply:
            allowed_states = [ResourceState.PLAN_COMPLETED, ResourceState.APPLY_FAILED]
            if resource.state not in allowed_states:
                raise (TfTaskConflict(f"Resource is not in desired state"))

            try:
                task_id = tf_apply.apply_async(
                    args=[resource_id, param.dict()], task_id=resource_id
                )
            except DuplicateTaskError as e:
                raise (CoreException.DuplicateTaskError(e.task_id))

            return dict(task_id=str(task_id))
        else:
            raise (CoreException.NotFound(f"Could not find any action {action}"))
