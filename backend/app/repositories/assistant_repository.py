from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.assistant_config import Assistant


async def get_assistant_by_id(assistant_id: int, db: AsyncSession):
    result = await db.execute(select(Assistant).where(Assistant.id == assistant_id))
    assistant = result.scalar_one_or_none()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistant