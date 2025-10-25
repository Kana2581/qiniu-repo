import base64
import traceback


from fastapi import APIRouter, Path, Body, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from backend.app.core.database import get_db_ctx, get_db
from backend.app.core.logging_config import get_logger
from backend.app.core.settings import settings
from backend.app.models.completion import CompletionRequest
from backend.app.services.agent_service import handle_chat_completion
import backend.app.utils.kobo_util as oss_util
from backend.app.services.chat_message_service import fetch_valid_langgraph_chat_messages
from backend.app.utils.redis_util import acquire_lock, release_lock
from backend.app.utils.voice_util import ASRClient

logger = get_logger(__name__)
router = APIRouter()


@router.post("/{session_id}/completions", description="Server-Sent Events (SSE) endpoint")
async def chat_completions(
    session_id: str = Path(..., description="The ID of the thread_id"),
    chat_message: CompletionRequest = Body(..., description="The content of the chat"),
) -> StreamingResponse:



    # 限流逻辑
    # if not await check_rate_limit(request):
    #     # 限流 SSE 错误格式响应
    #
    #     async def limited_event():
    #         logger.warning(f"{request.client.host}请求过于频繁")
    #         yield start_msg
    #         yield 'event: error\ndata: {"message":"Too many requests. Please try again later."}\n\n'
    #         yield end_msg
    #     return StreamingResponse(limited_event(), media_type="text/event-stream")

    if chat_message.type == "audio":
        audio_bytes = base64.b64decode(chat_message.content)
        oss_util.upload_data(audio_bytes,"audios/user"+chat_message.id,"audio/webm")
        user_audio_url =oss_util.get_private_url("audios/user"+chat_message.id)
        asr=ASRClient(settings.TTS_AND_ASR_API_KEY)
        content=asr.speech_to_text(user_audio_url)
    else:
        content=chat_message.content

    async def event_generator():
        start_msg = "event: start\ndata: {\"message\":\"stream start\"}\n\n"
        end_msg = "event: done\ndata: {\"message\":\"DONE\"}\n\n"
        yield start_msg

        async with get_db_ctx() as db:
            try:
                # 1. 加锁
                lock_value = await acquire_lock(session_id)
                if not lock_value:
                    logger.warning(f"failed to acquire lock for session {session_id}")
                    raise ValueError(f"failed to acquire lock for session {session_id}")
                #验证是否有session
                async for chunk in handle_chat_completion(thread_id=session_id,content=content,id=chat_message.id,db=db):
                    yield chunk


            except Exception as e:
                await db.rollback()
                tb_str = traceback.format_exc()  # 获取完整堆栈信息字符串
                logger.error(f"SSE chat generation failed: {e}\nTraceback:\n{tb_str}")
                yield "event: error\ndata: {\"message\":\"Internal server error occurred.\"}\n\n"
            finally:
                # 3. 释放锁
                if lock_value:  # 检查，锁有可能已经过期
                    try:
                        released = await release_lock(session_id, lock_value)
                        if not released:
                            logger.warning(f"[Lock] Failed to release lock for session_id={session_id}")
                    except Exception as e:
                        logger.error(f"[Lock] Exception during lock release: {e}")

                yield end_msg
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/{session_id}/messages/")
async def list_messages(session_id: str = Path(..., description="线程 ID"),db: AsyncSession = Depends(get_db)):
    """获取指定线程的聊天记录"""
    messages=await fetch_valid_langgraph_chat_messages(session_id,db,100)

    return {"messages":messages}