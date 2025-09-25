import os, ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine.url import make_url

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///planner.db")

Base = declarative_base()

engine_kwargs = {"echo": False, "pool_pre_ping": True}
url = make_url(DATABASE_URL)

# Для asyncpg передаём SSL-контекст явно
if url.drivername == "postgresql+asyncpg":
    engine_kwargs["connect_args"] = {"ssl": ssl.create_default_context()}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

