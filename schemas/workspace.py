from datetime import datetime

from pydantic import BaseModel, UUID4


class WorkspaceBase(BaseModel):
    name: str
    provider: str


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceInDB(WorkspaceBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
