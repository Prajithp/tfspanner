import uuid
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import UUID4
from models.workspace import Workspace as WorkspaceModel
from schema.workspace import WorkspaceIn

class Workspace(object):
    def __init__(self, db: Session):
        self.db = db

    def list(self, workspace_id: Optional[UUID4] = None):
        workspaces = None
        if workspace_id is not None:
            workspaces = self.db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
        else:
            workspaces = self.db.query(WorkspaceModel).all()
        return workspaces
    
    def create(self, workspace: WorkspaceIn):
        workspace = WorkspaceModel(name = workspace.name, provider = workspace.provider)
        self.db.add(workspace)
        self.db.flush()
        self.db.commit()
        self.db.refresh(workspace)
        return workspace
