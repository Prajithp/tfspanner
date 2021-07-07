from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from config.settings import settings
from contextlib import contextmanager

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_size=5, max_overflow=0)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)

Base = declarative_base()


@contextmanager
def db_session_scope() -> Iterator[Session]:
    db = session()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def db_session() -> Iterator[Session]:
    db = session()
    try:
        yield db
    finally:
        db.close()


async def init_tables() -> None:
    Base.metadata.create_all(bind=engine)
