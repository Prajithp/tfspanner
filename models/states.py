from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import datetime
from config.database import Base

class States(Base):
    __tablename__ = "states"

    id         = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    state      = Column(JSON, default={})
    project_id = Column(UUID(as_uuid=True), ForeignKey('project.id'))
    is_locked  = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return self.id
