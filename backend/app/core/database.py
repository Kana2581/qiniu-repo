
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Any, AsyncGenerator
from backend.app.core.connection import async_session
from contextlib import asynccontextmanager
# FastAPI 用的
# 用于 FastAPI 路由中依赖注入

Base = declarative_base()
# 依赖注入：获取数据库会话
async def get_db():
    async with async_session() as session:
        yield session
@asynccontextmanager
async def get_db_ctx():
    async with async_session() as session:

        yield session