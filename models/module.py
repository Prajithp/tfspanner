import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
from config.database import Base


class Module(Base):
    __tablename__ = "module"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(256), nullable=False)
    source = Column(String(256), nullable=False)
    variables = Column(JSON, default={})
    outputs = Column(JSON, default={})

    def __repr__(self):
        return self.id
