import os
from typing import Any
from pydantic.types import UUID4
from python_terraform import TerraformCommandError

from core.templating import Renderer
from core.worker import TfWorker
from schemas.resource import ResourceInDB, ResourceState
from models.resource import Resource
from utils.logger import getLogger
from config.celery import celery_app as app
from config.database import db_session
from config.redis import redis_session
from celery_singleton import Singleton

logger = getLogger(__name__)


def _update_state(db, resource_id, state):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    resource.state = state
    db.commit()


@app.task(base=Singleton, name="terraform_plan", bind=True)
def tf_plan(self, resource_id: str) -> Any:
    session = next(db_session())

    resource_obj = session.query(Resource).filter(Resource.id == resource_id).first()
    resource = ResourceInDB.from_orm(resource_obj)

    resource_id = str(resource.id)
    with Renderer(resource_id=resource_id) as r:
        r.context = resource
        _, dir = r.render()
        try:
            _update_state(session, resource_id, ResourceState.PLAN_RUNNING)
            with TfWorker(workspace=dir) as worker:
                logger.info(f"Running Terraform apply for {resource_id}")

                redis = next(redis_session())
                channel = resource_id
                worker.stream = lambda m: redis.publish(channel, m)

                rc, stdout, stderr = worker.plan()
                if rc == 1:
                    _update_state(session, resource_id, ResourceState.PLAN_FAILED)
                    return False

                _update_state(session, resource_id, ResourceState.PLAN_COMPLETED)
        except Exception as e:
            logger.exception(f"Terraform plan failed with {e}")
            _update_state(session, resource_id, ResourceState.PLAN_FAILED)
            return None

    return True


@app.task(base=Singleton, name="terraform_apply", bind=True)
def tf_apply(self, resource_id: str) -> Any:
    session = next(db_session())

    resource_obj = session.query(Resource).filter(Resource.id == resource_id).first()
    resource = ResourceInDB.from_orm(resource_obj)
    if (
        resource.user_approved == False
        or resource.state != ResourceState.PLAN_COMPLETED
    ):
        logger.error("Stack should be approved by user and should complete the plan")
        return False

    resource_id = str(resource.id)
    with Renderer(resource_id=resource_id) as r:
        r.context = resource
        _, dir = r.render()
        try:
            _update_state(session, resource_id, ResourceState.APPLY_RUNNING)
            with TfWorker(workspace=dir) as worker:
                logger.info(f"Running Terraform apply for {resource_id}")

                redis = next(redis_session())
                channel = resource_id
                worker.stream = lambda m: redis.publish(channel, m)

                rc, stdout, stderr = worker.apply()
                if rc == 1:
                    _update_state(session, resource_id, ResourceState.APPLY_FAILED)
                    return False

                resource = (
                    session.query(Resource).filter(Resource.id == resource_id).first()
                )
                output = worker.output_dict()
                if output:
                    resource.outputs = output
                resource.state = ResourceState.APPLY_COMPLETED
                session.commit()
        except Exception as e:
            logger.exception(f"Terraform apply failed with {e}")
            _update_state(session, resource_id, ResourceState.APPLY_FAILED)
            return None

    return True
