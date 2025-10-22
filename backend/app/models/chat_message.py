

from backend.app.core.database import Base




from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, JSON
)
from datetime import datetime
import enum


# 定义枚举类型
class MessageType(str, enum.Enum):
    text = "text"
    image = "image"
    code = "code"
    other = "other"


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id，自增")


    type = Column(String(32), nullable=False, comment="文本类型")

    content = Column(Text, nullable=False, comment="文本聊天内容")
    artifact = Column(Text, comment="生成的副产物（如代码、文档等）")

    thread_id = Column(String(64), nullable=False, comment="属于哪个对话线程")

    # SQLite 也支持 JSON 类型（底层是 TEXT 存储）
    tool_calls = Column(JSON, comment="工具调用信息（JSON格式）")

    langgraph_id = Column(String(64),unique=True, nullable=False, comment="LangGraph 节点 UUID")
    tool_call_id = Column(String(64), comment="工具调用ID，引用langgraph_id")
    name = Column(String(255), comment="工具调用名")
    message_group_id = Column(String(64), comment="消息分组ID")

    # SQLite 用 DateTime + default
    created_at = Column(DateTime, default=datetime.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), nullable=False, comment="更新时间")
