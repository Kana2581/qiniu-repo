from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.files_manager_agent.graph import get_file_agent
from backend.app.core.settings import settings
from backend.app.repositories.assistant_repository import get_assistant_by_id
from backend.app.repositories.session_repository import get_session
from backend.app.schemas.model_config import ModelConfig
from backend.app.schemas.voice_config import VoiceConfigBase
from backend.app.services.chat_message_service import (
    fetch_valid_langgraph_chat_messages,
    save_chat_messages_batch
)
from backend.app.utils.agent_util import (
    chat_messages_base2base_message,
    base_message2chat_messages_base,
    sse_format,
    voice_prompts,
    base64_format
)
from backend.app.utils.voice_util import (
    TTSClient,
    text_to_speech_segments,
    merge_audio_base64_segments
)
import backend.app.utils.kobo_util as oss_util


async def handle_chat_completion(id: str, thread_id: str, content: str, db: AsyncSession):
    """
    处理聊天内容生成的核心逻辑，支持正常新增消息与重新生成（覆盖）消息两种模式。
    """
    # 1. 获取会话元数据
    session = await get_session(db, thread_id)
    if session is None:
        raise HTTPException(400, "no session")

    assistant_orm = await get_assistant_by_id(session.assistant_id, db)

    # 2. 构建模型执行所需配置
    base_file_path = assistant_orm.base_file_path
    system_type = assistant_orm.system_type

    voice_config=VoiceConfigBase.model_validate(assistant_orm)
    model_config = ModelConfig.model_validate(assistant_orm)

    graph = get_file_agent(**model_config.model_dump(), system_type=system_type)

    # 3. 取历史上下文消息（窗口限制以避免上下文溢出）
    window_size = assistant_orm.window_size
    chat_message_bases = await fetch_valid_langgraph_chat_messages(
        session_id=thread_id,
        db=db,
        windows_size=window_size
    )
    messages = chat_messages_base2base_message(chat_message_bases)

    # 4. 校验输入
    if not content:
        raise HTTPException(400, "no messages or no voice")

    # 新增用户输入消息
    user_message = HumanMessage(content=content, id=id)
    messages.append(user_message)

    # 用于存储待写入数据库的消息与对应的语音 keys
    messages_pending = [user_message]
    tts_key_pending = [None]
    # 初始化 TTS 客户端
    tts = TTSClient(settings.TTS_AND_ASR_API_KEY, **voice_config.model_dump())

    # 流式 Token 及 TTS 语音缓存
    stream_tokens = []
    audio_segments = []

    # 5. 执行 LLM Graph，启用流式更新
    async for update_type, chunk in graph.astream(
        input={"messages": messages, "base_file_path": base_file_path},
        stream_mode=["updates", "messages"]
    ):
        # -------------------------- #
        # 更新类型：模型完整响应（分段）
        # -------------------------- #
        if update_type == "updates":
            only_key = next(iter(chunk))
            res_message = chunk[only_key]['messages'][-1]
            messages_pending.append(res_message)

            tts_key = None

            # 若 AI 消息生成完成，合并现有全部音频段并上传
            if isinstance(res_message, AIMessage) and res_message.content:
                merged_audio = merge_audio_base64_segments(audio_segments)
                if merged_audio:
                    tts_key = res_message.id + ".wav"
                    oss_util.upload_data(merged_audio, tts_key, mime_type="audio/wav")

            # 如果包含工具调用，追加语音化提示
            if isinstance(res_message, AIMessage) and res_message.tool_calls:
                tool_text = "".join(voice_prompts[t["name"]] for t in res_message.tool_calls)
                tool_audio = tts.text_to_speech(tool_text)
                yield base64_format(tool_audio)

            tts_key_pending.append(tts_key)

            # 推送 AI 文本消息 SSE
            if isinstance(res_message, AIMessage):
                yield sse_format(res_message, tts_key)
            # 清空tokens缓存和消息缓存
            stream_tokens.clear()
            audio_segments.clear()

        # -------------------------- #
        # 流类型：逐 Token 输出 + TTS 流式片段
        # -------------------------- #
        else:
            tmp_message = chunk[0]

            if isinstance(tmp_message, AIMessageChunk) and tmp_message.content:
                stream_tokens.append(tmp_message.content)

                # 按可拆分语音片段处理
                new_segments, remain = text_to_speech_segments(stream_tokens, tts.text_to_speech)

                for seg in new_segments:
                    yield base64_format(seg)
                    audio_segments.append(seg)

                stream_tokens = [remain]

    # 6. 转回 ORM 对象，插入数据库
    new_chat_message_bases = base_message2chat_messages_base(messages_pending, tts_key_pending)
    await save_chat_messages_batch(messages=new_chat_message_bases, db=db, thread_id=thread_id)
    await db.commit()  # 提交操作，确保事务生效
