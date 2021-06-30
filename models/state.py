import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import datetime
from config.database import Base


class State(Base):
    __tablename__ = "state"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    state = Column(JSON, default={})
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspace.id"), primary_key=True, nullable=False
    )
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self):
        return self.id
