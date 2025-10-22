from typing import List

from fastapi import HTTPException
from pydantic_core import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
from backend.app.core.logging_config import get_logger
from backend.app.enums.error.app_error import AppError
from backend.app.models.chat_message import ChatMessage
from backend.app.repositories.chat_message_repository import insert_messages_batch, insert_message, get_messages_by_thread_id
from backend.app.schemas.chat_message import ChatMessageBase

logger = get_logger(__name__)
async def fetch_valid_langgraph_chat_messages(session_id: str, db: AsyncSession,windows_size:int,langgraph_id:str=None) -> List[ChatMessageBase]:
    """
    服务层：获取指定会话的有效聊天消息，并转换为 Pydantic 模型对象列表。

    参数:
        session_id: 聊天会话 ID
        db: 数据库异步会话对象
        windows_size: 滑动窗口大小（+1 是为了多取一条供后续过滤）
        langgraph_id: 可选参数，用于指定起始的 langgraph 节点 ID

    返回:
        List[ChatMessageBase]: 聊天消息列表（Pydantic 格式）

    异常:
        HTTPException: 若模型转换失败或数据异常，则抛出 500 错误
    """
    # 获取原始聊天消息（含 tool 类型），预留多一条供上下文过滤
    chat_messages = await get_messages_by_thread_id(db, session_id,windows_size,langgraph_id)
    # 从第一个非 tool 类型消息开始截取，避免 GPT 报错（因为开头不能是 tool）
    try:
        # 转换为标准 Pydantic 对象列表
        return [ChatMessageBase.model_validate(msg) for msg in chat_messages]
    except ValidationError as e:
        # 转换失败时记录日志并抛出异常
        logger.error(f"session id {session_id} windows_size {windows_size} Failed to convert chat message format: {e}")
        raise HTTPException(
            status_code=500,
            detail={"code":AppError.INTERNAL_SERVER_ERROR.code(), "message": AppError.INTERNAL_SERVER_ERROR.message()}

        )
async def save_chat_messages_batch(
    messages: list[ChatMessageBase], db: AsyncSession,
    thread_id:str,
) :
    """
    批量保存聊天消息至数据库。

    参数:
        messages: 聊天消息列表（Pydantic 格式）
        db: 异步数据库会话对象
        user_id: 发送消息的用户 ID
        user_name: 用户名称
        session_id: 所属聊天会话 ID
        user_type: 用户类型（如 0=普通用户，1=HR 等）

    返回:
        无（直接写入数据库）
    """
    now = datetime.now()
    objs = [
        ChatMessage(


            type=msg.type,
            content=msg.content,
            tool_calls=msg.tool_calls,
            created_at=now,
            updated_at=now,
            thread_id=thread_id,
            langgraph_id=msg.id,
            tool_call_id=msg.tool_call_id,
            name=msg.name,
            message_group_id=msg.message_group_id,
            artifact=msg.artifact,
        )
        for msg in messages
    ]
    # 批量插入数据库
    await insert_messages_batch(db=db, messages=objs)

async def save_chat_message(
    message: ChatMessageBase, db: AsyncSession,    user_id,
    user_name:str,
    thread_id:str,
    user_type:int,

) :
    """
    批量保存聊天消息至数据库。

    参数:
        messages: 聊天消息列表（Pydantic 格式）
        db: 异步数据库会话对象
        user_id: 发送消息的用户 ID
        user_name: 用户名称
        session_id: 所属聊天会话 ID
        user_type: 用户类型（如 0=普通用户，1=HR 等）

    返回:
        无（直接写入数据库）
    """
    now = datetime.now()

    obj=ChatMessage(

            type=message.type,
            content=message.content,
            tool_calls=message.tool_calls,
            created_at=now,
            updated_at=now,
            thread_id=thread_id,
            langgraph_id=message.id,
            tool_call_id=message.tool_call_id,
            name=message.name,
        )

    # 批量插入数据库
    await insert_message(db=db, message=obj)