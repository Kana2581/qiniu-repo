from fastapi import APIRouter

from backend.app.routers import base_chat,chat_assistant,session,oss


router = APIRouter()


router.include_router(base_chat.router, prefix="/chats", tags=["chats"])


router.include_router(chat_assistant.router, prefix="/assistants", tags=["assistants"])

router.include_router(session.router, prefix="/session", tags=["session"])

router.include_router(oss.router, prefix="/oss", tags=["oss"])