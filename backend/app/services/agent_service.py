from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage, message_to_dict, ToolMessage
from langchain_core.messages.tool import tool_call
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.files_manager_agent.graph import  get_file_agent

from backend.app.core.settings import settings
from backend.app.repositories.assistant_repository import get_assistant_by_id
from backend.app.repositories.session_repository import get_session
from backend.app.schemas.assistant_config import AssistantResponse
from backend.app.schemas.model_config import ModelConfig

from backend.app.services.chat_message_service import fetch_valid_langgraph_chat_messages, save_chat_messages_batch
from backend.app.utils.agent_util import chat_messages_base2base_message, base_message2chat_messages_base, sse_format, \
    voice_prompts, base64_format
from backend.app.utils.voice_util import TTSClient
import backend.app.utils.kobo_util as oss_util

async def handle_chat_completion(id:str,thread_id: str,content: str,db: AsyncSession):
    """
    处理聊天内容生成的核心逻辑，支持正常新增消息与重新生成（覆盖）消息两种模式。
    """

    #thread = await fetch_valid_chat_thread(thread_id=thread_id, db=db)

    windows_size=30

    session=await get_session(db,thread_id)
    if session is None:
        raise HTTPException(400,"no session")
    assistant_orm=await get_assistant_by_id(session.assistant_id, db)
    print(assistant_orm)
    base_file_path=assistant_orm.base_file_path
    system_type=assistant_orm.system_type
    model_config=ModelConfig.model_validate(assistant_orm)
    graph = get_file_agent(**model_config.model_dump(),system_type=system_type)

    chat_message_bases = await fetch_valid_langgraph_chat_messages(session_id=thread_id, db=db,
                                                                   windows_size=windows_size)




    messages=chat_messages_base2base_message(chat_message_bases)
    messages += [HumanMessage(content=content, id=id)]
    messages_pending = [HumanMessage(content=content, id=id)]
    tts=TTSClient(settings.TTS_AND_ASR_API_KEY)
    tts_pending= [None]
    async for chunk in graph.astream(
            input={
                "messages": messages,
                "base_file_path":base_file_path,
            },
            stream_mode="updates"
    ):
        # 获取唯一的 key

        only_key = next(iter(chunk))
        res_message = chunk[only_key]['messages'][-1]

        messages_pending.append(res_message)
        tts_key=None

        if isinstance(res_message, AIMessage) and res_message.content is not None and res_message.content != "":
            base64=tts.text_to_speech(res_message.content)
            tts_bytes=tts.base64_to_bytes(base64)
            if tts_bytes:
                tts_key=res_message.id+".mp3"
                oss_util.upload_data(tts_bytes, tts_key)
        if isinstance(res_message,AIMessage) and len(res_message.tool_calls)>0:
            tool_call_string=""
            for tool_call in res_message.tool_calls:
                tool_call_string+=voice_prompts[tool_call["name"]]
            tool_call_base64=tts.text_to_speech(tool_call_string)
            print(tool_call_base64)
            yield base64_format(tool_call_base64)

        tts_pending.append(tts_key)

        yield sse_format(res_message,tts_key)

    new_chat_message_bases=base_message2chat_messages_base(messages_pending,tts_pending)
    #之后才会对表进行修改和插入，之前只有查找操作

    await save_chat_messages_batch(messages=new_chat_message_bases, db=db,thread_id=thread_id)
    await db.commit()  # 前两个操作都不提交，到这里事务才提交