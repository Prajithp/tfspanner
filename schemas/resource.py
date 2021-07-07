import json
from asyncpg.exceptions import DatetimeFieldOverflowError
from celery.app import task
from pydantic import BaseModel, UUID4, Json, validator
from typing import Any, List, Dict, Optional
from enum import Enum
from schemas.module import ModuleInDB
from schemas.workspace import WorkspaceInDB
from datetime import datetime


class ResourceBase(BaseModel):
    name: str
    module_id: UUID4
    variables: Dict[Any, Any]


class TfTaskInfo(BaseModel):
    task_id: str


class TfTaskAction(str, Enum):
    apply = "apply"
    plan = "plan"
    destroy = "destroy"


class TfTaskActionBody(BaseModel):
    parallelism: Optional[int] = None
    target: Optional[str] = None
    var: Optional[Dict] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceState(str, Enum):
    PENDING = "Pending"
    PLAN_FAILED = "PlanFailed"
    APPLY_FAILED = "ApplyFailed"
    PLAN_RUNNING = "PlanRunning"
    APPLY_RUNNING = "ApplyRunning"
    PLAN_COMPLETED = "PlanCompleted"
    APPLY_COMPLETED = "ApplyCompleted"


class ResourceInDB(ResourceBase):
    id: UUID4
    outputs: Dict[str, Any]
    module: ModuleInDB
    workspace: WorkspaceInDB
    state: ResourceState
    updated_at: datetime
    workspace_id: UUID4
    user_approved: bool

    class Config:
        orm_mode = True
        use_enum_values = True
