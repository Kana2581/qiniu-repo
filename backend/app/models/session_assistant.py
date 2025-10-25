from datetime import datetime, UTC

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey

from backend.app.core.database import Base


class SessionAssistant(Base):
    __tablename__ = "session"

    session_id = Column(String(64), primary_key=True, index=True)
    assistant_id = Column(
        Integer,
        ForeignKey("assistant.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))