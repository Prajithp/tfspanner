from datetime import datetime

import json
from pydantic import BaseModel, UUID4, Json, validator, Field
from typing import Any, List, Dict, Optional


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


class StateLockBase(BaseModel):
    id: str = Field(alias="ID")
    operation: str = Field(alias="Operation")
    info: Optional[str] = Field(alias="Info")
    who: Optional[str] = Field(alias="Who")
    version: Optional[str] = Field(alias="Version")
    created: Optional[str] = Field(alias="Created")
    path: Optional[str] = Field(alias="Path")


class StateLockCreate(StateLockBase):
    pass


class StateLockInDB(StateLockBase):
    workspace_id: UUID4

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
