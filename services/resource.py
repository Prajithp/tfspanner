from models.resource import Resource
from exceptions.core import CoreException
from services.base import CRUDBase


class ResourceService(CRUDBase):
    async def list_all(self):
        resources = self.db.query(Resource).order_by(Resource.id).all()
        if resources is None:
            raise (CoreException.NotFound(message=f"Not found workspace with id"))

        return resources
