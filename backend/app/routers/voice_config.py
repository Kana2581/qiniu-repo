from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.voice_config import VoiceConfig
from backend.app.schemas.voice_config import VoiceConfigBase

router = APIRouter()
@router.post("/voice", response_model=dict)
async def create_voice(data: VoiceConfigBase, db: AsyncSession = Depends(get_db)):
    config = VoiceConfig(**data.model_dump())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return {"id": config.id, "message": "语音配置已创建"}

# 编辑
@router.put("/voice/{id}", response_model=dict)
async def update_voice(id: int, data: VoiceConfigBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VoiceConfig).filter_by(id=id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="语音配置不存在")
    config.voice_type = data.voice_type
    config.speech_speed = data.speech_speed
    await db.commit()
    await db.refresh(config)
    return {"id": config.id, "message": "语音配置已更新"}

@router.get("/voice/list", response_model=dict)
async def get_voice_list(db: AsyncSession = Depends(get_db)):
    """
    获取所有语音配置列表
    """
    result = await db.execute(select(VoiceConfig))
    configs = result.scalars().all()

    data = [
        {
            "id": c.id,
            "voice_type": c.voice_type,
            "speech_speed": float(c.speech_speed) if c.speech_speed is not None else None,
        }
        for c in configs
    ]

    return {"total": len(data), "items": data}

@router.get("/voice/{id}", response_model=dict)
async def get_voice_config(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VoiceConfig).filter_by(id=id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="语音配置未找到")
    return {
        "id": config.id,
        "voice_type": config.voice_type,
        "speech_speed": float(config.speech_speed)
    }
