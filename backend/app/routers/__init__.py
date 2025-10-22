from fastapi import APIRouter

from backend.app.routers import base_chat,user_config


router = APIRouter()


router.include_router(base_chat.router, prefix="/chats", tags=["chats"])
router.include_router(user_config.router, prefix="/config", tags=["config"])