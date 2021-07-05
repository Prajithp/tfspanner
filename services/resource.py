from sys import stderr
from sqlalchemy.sql.elements import and_
from schemas.resource import ResourceCreate
from pydantic.types import UUID4
from models.resource import Resource
from exceptions.core import CoreException
from services.base import CRUDBase
from tasks.tfrunner import tf_plan
from celery_singleton.exceptions import DuplicateTaskError


class ResourceService(CRUDBase):
    async def list_all(self, workspace_id: UUID4):
        resources = (
            self.db.query(Resource)
            .filter(Resource.workspace_id == workspace_id)
            .order_by(Resource.updated_at)
            .all()
        )

        return resources

    async def resource_by_name_and_workspace(
        self, workspace_id: UUID4, resource_name: str
    ):
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

    async def create(self, workspace_id: UUID4, resource_info: ResourceCreate):
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

        resource_id = str(resource.id)
        try:
            task_id = tf_plan.apply_async(args=[resource_id], task_id=resource_id)
        except DuplicateTaskError as e:
            raise (CoreException.DuplicateTaskError(e.task_id))

        return resource
