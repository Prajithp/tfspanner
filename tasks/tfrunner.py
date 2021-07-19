import os
from typing import Any, Dict, List
from pydantic.types import UUID4
from python_terraform import TerraformCommandError
from sqlalchemy.engine import base

from core.templating import Renderer
from core.worker import TfWorker
from schemas.resource import ResourceInDB, ResourceState
from models.resource import Resource
from utils.logger import getLogger
from config.celery import celery_app as app
from config.database import db_session_scope
from config.redis import redis_session
from celery_singleton import Singleton

logger = getLogger(__name__)


def _update_state(resource_id: str, state: str) -> None:
    with db_session_scope() as session:
        resource = session.query(Resource).filter(Resource.id == resource_id).first()
        resource.state = state


@app.task(base=Singleton, name="terraform_plan", bind=True)
def tf_plan(self, resource_id: str, param: Dict) -> bool:
    with db_session_scope() as session:
        resource_obj = (
            session.query(Resource).filter(Resource.id == resource_id).first()
        )
        resource = ResourceInDB.from_orm(resource_obj)

    resource_id = str(resource.id)
    with Renderer(resource_id=resource_id) as r:
        r.context = resource
        _, dir = r.render()
        try:
            _update_state(resource_id, ResourceState.PLAN_RUNNING)
            with TfWorker(workspace=dir) as worker:
                logger.info(f"Running Terraform Plan for {resource_id}")

                redis = next(redis_session())
                channel = resource_id
                worker.stream = lambda m: redis.publish(channel, m)
                redis.publish(channel, f"Running Terraform plan for {resource_id}")

                rc, stdout, stderr = worker.plan(**param)
                if rc == 1:
                    _update_state(resource_id, ResourceState.PLAN_FAILED)
                    return False

                _update_state(resource_id, ResourceState.PLAN_COMPLETED)
        except Exception as e:
            logger.exception(f"Terraform plan failed with {e}")
            _update_state(resource_id, ResourceState.PLAN_FAILED)
            return None

    return True


@app.task(base=Singleton, name="terraform_apply", bind=True)
def tf_apply(self, resource_id: str, param: Dict) -> bool:

    with db_session_scope() as session:
        resource_obj = (
            session.query(Resource).filter(Resource.id == resource_id).first()
        )
        resource = ResourceInDB.from_orm(resource_obj)

    allowed_states = [ResourceState.PLAN_COMPLETED, ResourceState.APPLY_FAILED]
    if resource.state not in allowed_states:
        logger.error(f"Stack status should be {allowed_states}")
        return False

    resource_id = str(resource.id)
    with Renderer(resource_id=resource_id) as r:
        r.context = resource
        _, dir = r.render()
        try:
            _update_state(resource_id, ResourceState.APPLY_RUNNING)
            with TfWorker(workspace=dir) as worker:
                logger.info(f"Running Terraform apply for {resource_id}")

                redis = next(redis_session())
                channel = resource_id
                worker.stream = lambda m: redis.publish(channel, m)
                redis.publish(channel, f"Running Terraform apply for {resource_id}")

                rc, stdout, stderr = worker.apply(**param)
                if rc == 1:
                    _update_state(resource_id, ResourceState.APPLY_FAILED)
                    return False

                with db_session_scope() as session:
                    resource = (
                        session.query(Resource)
                        .filter(Resource.id == resource_id)
                        .first()
                    )
                    output = worker.output_dict()
                    if output:
                        resource.outputs = output
                        resource.state = ResourceState.APPLY_COMPLETED
        except Exception as e:
            logger.exception(f"Terraform apply failed with {e}")
            _update_state(resource_id, ResourceState.APPLY_FAILED)
            return None

    return True


@app.task(base=Singleton, name="terraform_destroy", bind=True)
def tf_destroy(self, resource_id: str, params: Dict) -> bool:
    with db_session_scope() as session:
        resource_obj = (
            session.query(Resource).filter(Resource.id == resource_id).first()
        )
        resource = ResourceInDB.from_orm(resource_obj)

    if resource.state not in ResourceState.APPLY_COMPLETED:
        logger.error("Stack status should be APPLY_COMPLETED")
        return False

    resource_id = str(resource.id)
    with Renderer(resource_id=resource_id) as r:
        r.context = resource
        _, dir = r.render()

        try:
            with TfWorker(workspace=dir) as worker:
                logger.info(f"Running Terraform destroy for {resource_id}")

                redis = next(redis_session())
                channel = resource_id
                worker.stream = lambda m: redis.publish(channel, m)
                redis.publish(channel, f"Running Terraform destroy for {resource_id}")

                rc, stdout, stderr = worker.destroy(**params)
                if rc == 1:
                    return False

                with db_session_scope() as session:
                    resource = (
                        session.query(Resource)
                        .filter(Resource.id == resource_id)
                        .delete()
                    )
                logger.info(f"Deleted resource {resource.name} from db")
        except Exception as e:
            logger.exception(f"Terraform destroy failed with {e}")
            return None

    return True
