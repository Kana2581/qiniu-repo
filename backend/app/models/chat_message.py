

from backend.app.core.database import Base




from sqlalchemy import (
    Column, Integer, String, Text, JSON, TIMESTAMP
)
from datetime import datetime, UTC


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id，自增")


    type = Column(String(32), nullable=False, comment="文本类型")

    content = Column(Text, nullable=False, comment="文本聊天内容")
    artifact = Column(Text, comment="生成的副产物（如代码、文档等）")

    thread_id = Column(String(64), nullable=False, comment="属于哪个对话线程")

    tool_calls = Column(JSON, comment="工具调用信息（JSON格式）")

    langgraph_id = Column(String(64),unique=True, nullable=False, comment="LangGraph 节点 UUID")
    tool_call_id = Column(String(64), comment="工具调用ID，引用langgraph_id")
    name = Column(String(255), comment="工具调用名")
    message_group_id = Column(String(64), comment="消息分组ID")
    tts_key=Column(String(255),comment="对象存储key",nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC), onupdate=datetime.now(UTC))
