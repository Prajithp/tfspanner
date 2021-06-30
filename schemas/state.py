from datetime import datetime

import json
from pydantic import BaseModel, UUID4, Json, validator
from typing import Any, List, Dict


class StateBase(BaseModel):
    pass


class StateInDB(StateBase):
    id: UUID4
    state: Json
    workspace_id: UUID4
    created_at: datetime
    updated_at: datetime

    @validator("state", pre=True)
    def decode_json(cls, v):
        if not isinstance(v, str):
            try:
                return json.dumps(v)
            except Exception as err:
                raise ValueError(f"Could not parse value into valid JSON: {err}")

    class Config:
        orm_mode = True


class TfState(BaseModel):
    version: int
    terraform_version: str
    serial: int
    lineage: str
    outputs: Dict
    resources: List[Any]


class TfResource(BaseModel):
    type: str
    name: str
    dependencies: List[Any]
    module: str
