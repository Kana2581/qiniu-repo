from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.session_assistant import SessionAssistant


async def create_or_update_session(db: AsyncSession, session_id: str, assistant_id: int):
    result = await db.execute(select(SessionAssistant).where(SessionAssistant.session_id == session_id))
    record = result.scalar_one_or_none()

    if record:
        record.assistant_id = assistant_id
        record.updated_at = datetime.now(UTC)
    else:
        record = SessionAssistant(session_id=session_id, assistant_id=assistant_id)
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record

async def get_session(db: AsyncSession, session_id: str):
    result = await db.execute(select(SessionAssistant).where(SessionAssistant.session_id == session_id))
    return result.scalar_one_or_none()

async def get_all_sessions(db: AsyncSession):
    result = await db.execute(select(SessionAssistant))
    return result.scalars().all()

async def delete_session(db: AsyncSession, session_id: str):
    result = await db.execute(select(SessionAssistant).where(SessionAssistant.session_id == session_id))
    record = result.scalar_one_or_none()
    if not record:
        return False
    await db.delete(record)
    await db.commit()
    return True