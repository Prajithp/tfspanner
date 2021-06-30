import json
from pydantic import BaseModel, UUID4, Json, validator
from typing import Any, List, Dict

from schemas.module import ModuleInDB
from schemas.workspace import WorkspaceInDB


class ResourceBase(BaseModel):
    name: str
    workspace_id: UUID4
    module_id: UUID4


class ResourceCreate(ResourceBase):
    pass


class ResourceInDB(ResourceBase):
    id: UUID4
    variables: Json
    outputs: Json
    module: ModuleInDB
    workspace: WorkspaceInDB

    @validator("outputs", pre=True)
    def outputs_decode_json(cls, v):
        if not isinstance(v, str):
            try:
                return json.dumps(v)
            except Exception as err:
                raise ValueError(f"Could not parse value into valid JSON: {err}")

    @validator("variables", pre=True)
    def variables_decode_json(cls, v):
        if not isinstance(v, str):
            try:
                return json.dumps(v)
            except Exception as err:
                raise ValueError(f"Could not parse value into valid JSON: {err}")

    class Config:
        orm_mode = True
