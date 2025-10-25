from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.repositories.session_repository import create_or_update_session, get_session, get_all_sessions, \
    delete_session
from backend.app.schemas.session_assistant import SessionAssistantCreate, SessionAssistantOut

# 新增或更新

router = APIRouter()
@router.post("/{session_id}", response_model=SessionAssistantOut)
async def create_or_update(session_id: str, body: SessionAssistantCreate, db: AsyncSession = Depends(get_db)):
    return await create_or_update_session(db, session_id, body.assistant_id)

# 查询单个
@router.get("/{session_id}", response_model=SessionAssistantOut)
async def get_one(session_id: str, db: AsyncSession = Depends(get_db)):
    record = await get_session(db, session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return record

# 查询全部
@router.get("/", response_model=List[SessionAssistantOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await get_all_sessions(db)

# 删除
@router.delete("/{session_id}")
async def delete_one(session_id: str, db: AsyncSession = Depends(get_db)):
    success = await delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Deleted successfully"}