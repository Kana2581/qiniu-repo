from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.assistant_config import Assistant
from backend.app.repositories.assistant_repository import get_assistant_by_id
from backend.app.schemas.assistant_config import AssistantCreate, AssistantResponse, AssistantUpdate

router = APIRouter()

# 创建或更新助手
@router.post("/", response_model=AssistantResponse)
async def create_assistant(assistant: AssistantCreate, db: AsyncSession = Depends(get_db)):
    db_assistant = Assistant(**assistant.model_dump())
    db.add(db_assistant)
    await db.commit()
    await db.refresh(db_assistant)
    return db_assistant

# 获取所有助手
@router.get("/", response_model=list[AssistantResponse])
async def list_assistants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assistant))
    return result.scalars().all()

# 根据ID获取助手
@router.get("/{assistant_id}", response_model=AssistantResponse)
async def get_assistant(assistant_id: int, db: AsyncSession = Depends(get_db)):
    return await get_assistant_by_id(assistant_id, db)

# 更新助手
@router.put("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(assistant_id: int, assistant_update: AssistantUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assistant).where(Assistant.id == assistant_id))
    assistant = result.scalar_one_or_none()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    for key, value in assistant_update.dict(exclude_unset=True).items():
        setattr(assistant, key, value)
    await db.commit()
    await db.refresh(assistant)
    return assistant

# 删除助手
@router.delete("/{assistant_id}", response_model=dict)
async def delete_assistant(assistant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assistant).where(Assistant.id == assistant_id))
    assistant = result.scalar_one_or_none()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    await db.delete(assistant)
    await db.commit()
    return {"message": "Assistant deleted successfully"}