from sqlalchemy.orm import relationship
import uuid

from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
from config.database import Base


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
        primary_key=True,
        nullable=False,
    )
    variables = Column(JSON, default={})
    module_id = Column(
        UUID(as_uuid=True),
        ForeignKey("module.id"),
        index=True,
        primary_key=True,
        nullable=False,
    )
    outputs = Column(JSON, default={})

    module = relationship("Module", backref="resources")
    workspace = relationship("Workspace", backref="resources")

    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="unique_resource_per_workspace"),
    )

    def __repr__(self):
        return self.id
