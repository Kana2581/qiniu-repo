import json
from typing import List

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage, message_to_dict

from backend.app.enums.message_type import MessageType
from backend.app.schemas.chat_message import ChatMessageBase


def base_message2chat_messages_base(messages: List[BaseMessage],tts_keys:List[str]) -> List[ChatMessageBase]:
    """
    将 LangChain 的 BaseMessage 列表转换为自定义的 ChatMessageBase 列表，方便数据库存储或业务处理。

    根据消息具体类型（HumanMessage, AIMessage, SystemMessage, ToolMessage）映射不同字段：
    - human: 普通用户消息
    - ai: AI 生成消息，可能包含 tool_calls（工具调用信息）
    - system: 系统消息
    - tool: 工具消息，带 name 和 tool_call_id
    对于未知类型，默认按 human 处理。
    """
    result = []
    for msg,tts_key in zip(messages,tts_keys):
        if isinstance(msg, HumanMessage):
            result.append(ChatMessageBase(
                content=msg.content,
                type="human",
                id=msg.id,
                tts_key=tts_key
            ))
        elif isinstance(msg, AIMessage):
            result.append(ChatMessageBase(
                content=msg.content,
                type="ai",
                id=msg.id,
                tool_calls=msg.tool_calls if msg.tool_calls else None,
                tts_key=tts_key

            ))
        elif isinstance(msg, SystemMessage):
            result.append(ChatMessageBase(
                content=msg.content,
                type="system",
                id=msg.id,
                tts_key=tts_key
            ))
        elif isinstance(msg, ToolMessage):
            result.append(ChatMessageBase(
                content=msg.content,
                type="tool",
                id=msg.id,
                name=msg.name,
                tool_call_id=msg.tool_call_id,
                artifact=msg.artifact,
                tts_key=tts_key
            ))
        else:
            # fallback: treat as human
            result.append(ChatMessageBase(
                content=msg.content,
                type="human",
                id=getattr(msg, "id", ""),
                tts_key=tts_key
            ))
    return result

def chat_messages_base2base_message(raw_messages:List[ChatMessageBase]) -> List[BaseMessage]:
    """
    将自定义的 ChatMessageBase 列表转换回 LangChain 的 BaseMessage 列表，方便调用 LangChain 或 LangGraph 流程。

    根据 type 字段选择创建对应的 LangChain 消息类实例：
    - human -> HumanMessage
    - ai -> AIMessage（反序列化 tool_calls）
    - system -> SystemMessage
    - tool -> ToolMessage（包含 name 和 tool_call_id）
    对于未知类型，默认按 HumanMessage 处理以保证兼容。
    """
    langchain_messages = []
    for msg in raw_messages:
        msg_type = msg.type

        if msg_type == MessageType.human:
            langchain_messages.append(HumanMessage(content=msg.content,id=msg.id))
        elif msg_type == MessageType.ai:

            langchain_messages.append(AIMessage(content=msg.content,id=msg.id,tool_calls=msg.tool_calls if msg.tool_calls else []) )
        elif msg_type == MessageType.system:
            langchain_messages.append(SystemMessage(content=msg.content,id=msg.id))
        elif msg_type == MessageType.tool:
            langchain_messages.append(ToolMessage(content=msg.content,id=msg.id,name=msg.name,tool_call_id=msg.tool_call_id,artifact=msg.artifact))
        else:
            # fallback: treat unknown type as human
            langchain_messages.append(HumanMessage(**msg.model_dump() ))

    return langchain_messages
def sse_format(chunk, tts_key:str=None):
    """
    将 AIMessageChunk 格式化为 SSE 响应格式，支持 metadata 可为空。
    """

    chunk_dict=message_to_dict(chunk)
    if tts_key:
        chunk_dict["data"]["tts_key"] = tts_key
    # 将 chunk 和 metadata 合并为一个字典
    data = {
        "chunk": chunk_dict
    }

    json_data = json.dumps(data)
    return f"event: message\ndata: {json_data}\n\n"
def base64_format(base64:str):
    """
    将 AIMessageChunk 格式化为 SSE 响应格式，支持 metadata 可为空。
    """
    data = {
        "base64": base64
    }
    json_data = json.dumps(data)
    return f"event: audio\ndata: {json_data}\n\n"

voice_prompts = {
    "write_file": "请稍后，正在准备进行写入文件操作。",
    "read_file": "请稍后，正在读取文件内容。",
    "show_tree": "请稍后，正在列出文件目录结构。",
    "delete_file": "请稍后，正在删除文件，请注意操作。",
    "open_file": "请稍后，正在打开文件。",
    "rename_path": "请稍后，正在重命名文件或文件夹。",
    "copy_path": "请稍后，正在复制文件或文件夹。",
    "move_path": "请稍后，正在移动文件或文件夹。",
    "run_command": "请稍后，正在执行系统命令。",
    "create_dir": "请稍后，正在创建新目录。"
}