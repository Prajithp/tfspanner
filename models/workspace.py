import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from config.database import Base

class Workspace(Base):
    __tablename__ = "workspace"

    id         = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    name       = Column(String(256), nullable=False, unique=True)
    provider   = Column(String(256), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)        

    def __repr__(self):
        return self.name
