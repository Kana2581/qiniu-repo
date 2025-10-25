from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, model_validator


class ChatMessageBase(BaseModel):
    content: Optional[str] = Field(None, description="文本聊天内容")
    type: Optional[str] = Field(None, description="文本类型（human:提问，ai: 回复 tool:工具）")
    tool_calls: Optional[List[Dict]] = Field(None, description="工具调用")

    # 注意：这个 id 实际上会使用 langgraph_id 映射
    id: str = Field(..., description="兼容框架id（映射 langgraph_id）")
    tool_call_id: Optional[str] = Field(None, description="工具调用id，引用 langgraph_id")
    name: Optional[str] = Field(None, description="工具调用名")
    artifact: Optional[str] = Field(None, description="artifact")
    tts_key:Optional[str]=Field(None,description="tts_key")
    parent_message_id: Optional[str] = Field(None, description="<UNK>ID")
    message_group_id: Optional[str] = Field(None, description="<UNK>ID")
    # ✅ 使用 model_validator 实现 langgraph_id 到 id 的映射
    @model_validator(mode="before")
    @classmethod
    def map_langgraph_id(cls, data: Any):
        if isinstance(data, dict):
            data = dict(data)  # 避免污染原始数据
            if "langgraph_id" in data:
                data["id"] = data["langgraph_id"]
        elif hasattr(data, "langgraph_id"):
            # ORM对象处理：copy属性避免直接改对象
            data_dict = data.__dict__.copy()
            data_dict["id"] = getattr(data, "langgraph_id")
            return data_dict
        return data

    model_config = {
        "from_attributes": True
    }