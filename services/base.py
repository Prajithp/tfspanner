from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import schema
from sqlalchemy.orm import Session, Query
from config.database import Base

Schema = TypeVar("Schema", bound=Base)


class CRUDBase(object):
    def __init__(self, db: Session) -> None:
        self.db = db

    def _query(self, model: Schema) -> Query:
        return self.db.query(model)

    def _create(self, model_obj: Schema) -> Schema:
        self.db.add(model_obj)
        self.db.commit()
        self.db.refresh(model_obj)
        return model_obj

    def _update(self, model_obj: Schema, **kwargs: dict) -> Schema:
        for field in kwargs:
            setattr(model_obj, field, kwargs[field])

        self.db.commit()
        self.db.refresh(model_obj)
        return model_obj
