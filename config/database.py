from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:test@localhost:5432/terraspanner"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)

async_session = sessionmaker(
    autocommit=False, autoflush=True,
    bind=engine, class_=AsyncSession
)

Base = declarative_base()

async def db_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def init_tables():
    async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.create_all)
