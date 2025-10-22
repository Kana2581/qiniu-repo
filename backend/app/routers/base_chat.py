import traceback
from typing import Optional

from fastapi import APIRouter, Path, Body
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from backend.app.core.database import get_db_ctx
from backend.app.core.logging_config import get_logger
from backend.app.services.agent_service import handle_chat_completion

logger = get_logger(__name__)
router = APIRouter()

class CompletionRequest(BaseModel):
    content: str = Field( description="用户输入的消息内容")
    id: str= Field( description="前端生成的 UUID（前端唯一标识消息）")

@router.post("/{session_id}/completions", description="Server-Sent Events (SSE) endpoint")
async def chat_completions(
    session_id: str = Path(..., description="The ID of the thread_id"),
    chat_message: CompletionRequest = Body(..., description="The content of the chat"),
) -> StreamingResponse:



    # 限流逻辑：放到视图头部
    # if not await check_rate_limit(request):
    #     # 限流 SSE 错误格式响应
    #
    #     async def limited_event():
    #         logger.warning(f"{request.client.host}请求过于频繁")
    #         yield start_msg
    #         yield 'event: error\ndata: {"message":"Too many requests. Please try again later."}\n\n'
    #         yield end_msg
    #     return StreamingResponse(limited_event(), media_type="text/event-stream")



    async def event_generator():
        start_msg = "event: start\ndata: {\"message\":\"stream start\"}\n\n"
        end_msg = "event: done\ndata: {\"message\":\"DONE\"}\n\n"
        yield start_msg
        async with get_db_ctx() as db:
            try:
                #验证是否有session
                #await fetch_valid_chat_session(session_id=session_id, db=db)
                async for chunk in handle_chat_completion(thread_id=session_id,content=chat_message.content,id=chat_message.id,db=db):
                    yield chunk


            except Exception as e:
                await db.rollback()
                tb_str = traceback.format_exc()  # 获取完整堆栈信息字符串
                logger.error(f"SSE chat generation failed: {e}\nTraceback:\n{tb_str}")
                yield "event: error\ndata: {\"message\":\"Internal server error occurred.\"}\n\n"
            finally:
                yield end_msg
    return StreamingResponse(event_generator(), media_type="text/event-stream")