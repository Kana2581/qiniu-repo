


from typing import Optional, List
from sqlalchemy import select, update, text, Result

from backend.app.models.chat_message import ChatMessage

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.engine import Result

from typing import List
import json
async def insert_message(
    message: ChatMessage,
    db: AsyncSession,
):
    db.add(message)



async def insert_messages_batch(

    messages: list[ChatMessage],
    db: AsyncSession,
):
    """
      批量插入一组 ChatMessage 消息对象到数据库会话中（未自动提交）。

      参数:
          messages (list[ChatMessage]): 需要插入的消息对象列表。
          db (AsyncSession): 异步数据库会话对象。

      注意事项:
          - 此操作仅将数据加入到当前事务中，并未自动提交（需调用方手动 db.commit()）。
          - 若消息已包含主键 ID，可能触发冲突，请确保数据结构合法。
      """
    # 使用 SQLAlchemy 提供的 add_all 方法将所有消息对象添加到数据库会话中
    db.add_all(messages)






async def get_messages_by_thread_id(
        db: AsyncSession,
        thread_id: str,
        limit: int,
        langgraph_id: Optional[str] = None
) -> list[ChatMessage]:
    """
    根据会话 ID 获取对应的聊天消息记录（支持基于 langgraph_id 的历史回溯查询）。

    参数:
        db (AsyncSession): 异步数据库会话对象。
        session_id (str): 会话的唯一标识。
        limit (int): 限制返回的消息数量。
        langgraph_id (Optional[str]): （可选）若提供，则只返回在此消息之前的消息。

    返回:
        list[ChatMessage]: 返回按时间正序排列的消息列表。
    """

    # 如果提供了 langgraph_id，则查找对应的消息 ID（ChatMessage.id）
    before_id = None
    if langgraph_id:

        return await get_message_chain(db, langgraph_id, thread_id)

    # 构建主查询：按 session_id 获取未被逻辑删除的消息
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread_id)

    )

    # 如果设置了 before_id，则只取比该 ID 更早的消息
    if before_id is not None:
        stmt = stmt.where(ChatMessage.id < before_id)

    # 按消息 ID 降序排列（从最新往前取），并限制返回数量
    stmt = stmt.order_by(ChatMessage.id.desc()).limit(limit)

    # 执行查询并获取结果
    result = await db.execute(stmt)
    messages = result.scalars().all()

    # 返回按 ID 升序（即时间正序）的消息列表
    return list(reversed(messages))



async def get_message_chain(db: AsyncSession, langgraph_id: str,thread_id:str) -> List[ChatMessage]:
    sql = text("""
        WITH RECURSIVE message_chain AS (
            SELECT * FROM chat_message WHERE langgraph_id = :langgraph_id and thread_id = :thread_id
            UNION ALL
            SELECT m.* FROM chat_message m
            JOIN message_chain c ON m.langgraph_id = c.parent_message_id
        )
        SELECT * FROM message_chain
        ORDER BY id ASC;
    """)

    result: Result = await db.execute(sql, {"langgraph_id": langgraph_id, "thread_id": thread_id})

    rows = result.mappings().all()

    messages = []
    for row in rows:
        row_dict = dict(row)

        # 👇 修正 JSON 字段（防止 tool_calls 是字符串 'null'）
        tool_calls = row_dict.get("tool_calls")
        if isinstance(tool_calls, str):
            try:
                row_dict["tool_calls"] = json.loads(tool_calls)
            except json.JSONDecodeError:
                row_dict["tool_calls"] = None

        messages.append(ChatMessage(**row_dict))

    return messages


async def get_ids_after_langgraph_id(
    db: AsyncSession,
    session_id: str,
    langgraph_id: str
) -> List[int]:
    """
    获取指定 langgraph_id 对应消息及其之后的所有消息 ID（同一 session 中，未被逻辑删除）。

    参数:
        db (AsyncSession): 异步数据库会话对象。
        session_id (str): 聊天会话的唯一标识。
        langgraph_id (str): 起始消息的 langgraph 唯一标识。

    返回:
        List[int]: 所有满足条件的消息 ID 列表（按 ID 升序排列）。
    """

    # 查找 langgraph_id 对应的消息 ID（仅限有效消息）
    sub_stmt = (
        select(ChatMessage.id)

        .where(ChatMessage.langgraph_id == langgraph_id,ChatMessage.is_effect == 0)
        .limit(1)
    )
    result = await db.execute(sub_stmt)
    current_id = result.scalar_one_or_none()
    # 若未找到对应消息，说明 langgraph_id 不存在或已被删除，直接返回空列表
    if current_id is None:
        return []  # 没找到则返回空列表

    # 查找当前消息及其之后（id >= current_id）在同一 session 内的所有有效消息 ID
    stmt = (
        select(ChatMessage.id)
        .where(ChatMessage.session_id == session_id)
        .where(ChatMessage.is_effect == 0)
        .where(ChatMessage.id >= current_id)
        .order_by(ChatMessage.id)
    )
    # 执行查询，获取 ID 列表
    result = await db.execute(stmt)
    ids = result.scalars().all()

    return ids

async def get_message_by_langgraph_id(
    db: AsyncSession,
    langgraph_id: str
) -> ChatMessage|None:
    """
    根据 langgraph_id 查询对应的消息对象。

    参数:
        db (AsyncSession): 异步数据库会话对象。
        langgraph_id (str): 唯一标识某条消息的 langgraph_id。

    返回:
        ChatMessage | None: 如果存在匹配记录，则返回该消息对象；否则返回 None。
    """
    # 构造查询语句，根据 langgraph_id 查找消息记录
    sub_stmt = (
        select(ChatMessage)
        .where(ChatMessage.langgraph_id == langgraph_id)
        .limit(1)
    )
    # 执行查询
    result = await db.execute(sub_stmt)
    # 获取结果（如果没有匹配记录则为 None）
    message = result.scalar_one_or_none()
    return message

async def delete_messages_by_ids(
    db: AsyncSession,
    ids: List[int]
) -> None:
    """
    根据给定的消息 ID 列表逻辑删除对应消息（设置 is_effect = 1）。

    参数:
        db (AsyncSession): 异步数据库会话对象。
        ids (List[int]): 需要删除的消息 ID 列表。

    返回:
        None
    """
    if not ids:
        return  # 空列表直接返回，不执行操作
    # 构造更新语句，将指定 ID 列表中的消息逻辑删除（is_effect = 1）
    stmt = (
        update(ChatMessage)
        .where(ChatMessage.id.in_(ids))
        .values(is_effect=1)
    )
    # 执行更新操作（注意：需要外部手动 commit）
    await db.execute(stmt)