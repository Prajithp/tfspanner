from datetime import datetime

from pydantic import BaseModel, UUID4

class WorkspaceBase(BaseModel):
    name: str
    provider: str
    
class WorkspaceIn(WorkspaceBase):
    pass

class Workspace(WorkspaceBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
