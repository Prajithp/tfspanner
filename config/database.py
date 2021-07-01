from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
)

session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

scoped_db_session = scoped_session(session)

Base = declarative_base()


def db_session():
    db = session()
    try:
        yield db
    finally:
        db.close()


async def init_tables():
    Base.metadata.create_all(bind=engine)
