from sqlalchemy.orm import relationship
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    ForeignKey,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from schemas.resource import ResourceState
from datetime import datetime
from config.database import Base
from models.workspace import Workspace
from models.module import Module


class Resource(Base):
    __tablename__ = "resource"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(256), nullable=False)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspace.id"),
        index=True,
        nullable=False,
    )
    variables = Column(JSON, default={})
    module_id = Column(
        UUID(as_uuid=True),
        ForeignKey("module.id"),
        index=True,
        nullable=False,
    )
    outputs = Column(JSON, default={})
    state = Column(Enum(ResourceState), default=ResourceState.PENDING)
    user_approved = Column(Boolean, default=False)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    module = relationship("Module", backref="resources")
    workspace = relationship("Workspace", backref="resources")

    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="unique_resource_per_workspace"),
    )

    def __repr__(self):
        return self.id
