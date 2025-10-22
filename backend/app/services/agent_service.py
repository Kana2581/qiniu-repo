from langchain_core.messages import AIMessage, HumanMessage, message_to_dict
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.files_manager_agent.graph import file_agent
from backend.app.agents.supervisor_agent.graph import supervisor_agent
from backend.app.core.logging_config import get_logger


from backend.app.services.chat_message_service import fetch_valid_langgraph_chat_messages, save_chat_messages_batch
from backend.app.utils.agent_util import chat_messages_base2base_message, base_message2chat_messages_base, sse_format


async def handle_chat_completion(id:str,thread_id: str,content: str,db: AsyncSession):
    """
    处理聊天内容生成的核心逻辑，支持正常新增消息与重新生成（覆盖）消息两种模式。
    """

    #thread = await fetch_valid_chat_thread(thread_id=thread_id, db=db)

    windows_size=30

    chat_message_bases = await fetch_valid_langgraph_chat_messages(session_id=thread_id, db=db,
                                                                   windows_size=windows_size)


    graph = file_agent


    messages=chat_messages_base2base_message(chat_message_bases)
    messages += [HumanMessage(content=content, id=id)]
    messages_pending = [HumanMessage(content=content, id=id)]

    async for chunk in graph.astream(
            input={
                "messages": messages,
            },
            stream_mode="updates"
    ):
        # 获取唯一的 key
        only_key = next(iter(chunk))
        res_message = chunk[only_key]['messages'][-1]

        messages_pending.append(res_message)
        yield sse_format(res_message)


    new_chat_message_bases=base_message2chat_messages_base(messages_pending)
    #之后才会对表进行修改和插入，之前只有查找操作

    await save_chat_messages_batch(messages=new_chat_message_bases, db=db,thread_id=thread_id)
    await db.commit()  # 前两个操作都不提交，到这里事务才提交