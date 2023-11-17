from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DB_USER = config("DB_USER", default="user")
DB_PASS = config("DB_PASS", default="pass")
DB_NAME = config("DB_NAME", default="name")
DB_PORT = config("DB_PORT", default="5432")

engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@127.0.0.1:{DB_PORT}/{DB_NAME}")
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
