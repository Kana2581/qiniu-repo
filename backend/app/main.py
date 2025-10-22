
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from backend.app.core.connection import engine
from backend.app.core.database import Base
from backend.app.routers import router as api_router

from backend.app.middlewares.logging import LoggingMiddleware

from backend.app.routers.base_chat import router
app = FastAPI()
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')



app.add_middleware(
    LoggingMiddleware,
    skip_paths=["/docs", "/openapi.json", "/favicon.ico"],
    log_body=True,  # 根据需要设置为 True/False
    log_response=True,
)
# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/v1")
class Item(BaseModel):
    text: str
# 在应用启动时建表（可选）

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

