import json
from pydantic import BaseModel, UUID4, Json, validator
from typing import Any, List, Dict


class ModuleBase(BaseModel):
    name: str
    source: str


class ModuleCreate(ModuleBase):
    pass


class ModuleInDB(ModuleBase):
    id: UUID4
    variables: Json
    outputs: Json

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
