from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from backend.app.core.database import get_db
from backend.app.models.chat_config import ChatConfig
from backend.app.schemas.chat_config import ChatConfigBase

router = APIRouter()
@router.post("/chat", response_model=dict)
async def create_or_update_chat(data: ChatConfigBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatConfig).filter_by(model_id=data.model_id))
    config = result.scalars().first()

    if config:
        config.prompt_text = data.prompt_text
        config.window_size = data.window_size
    else:
        config = ChatConfig(**data.model_dump())
        db.add(config)

    await db.commit()
    await db.refresh(config)
    return {"id": config.id, "message": "聊天配置已创建或更新"}


@router.get("/chat/{id}", response_model=dict)
async def get_chat_config(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatConfig).filter_by(id=id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="聊天配置未找到")
    return {
        "id": config.id,
        "model_id": config.model_id,
        "prompt_text": config.prompt_text,
        "window_size": config.window_size
    }