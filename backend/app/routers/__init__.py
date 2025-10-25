from fastapi import APIRouter

from backend.app.routers import base_chat,user_config,voice_config,chat_assistant,session,oss


router = APIRouter()


router.include_router(base_chat.router, prefix="/chats", tags=["chats"])

# router.include_router(chat_config.router, prefix="/config", tags=["config"])
#
# router.include_router(model_config.router, prefix="/config", tags=["config"])
#
# router.include_router(voice_config.router, prefix="/config", tags=["config"])

router.include_router(chat_assistant.router, prefix="/assistants", tags=["assistants"])

router.include_router(session.router, prefix="/session", tags=["session"])

router.include_router(oss.router, prefix="/oss", tags=["oss"])