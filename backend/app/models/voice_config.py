from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP

from backend.app.core.database import Base


class VoiceConfig(Base):
    __tablename__ = "voice_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    voice_type = Column(String(100))
    speech_speed = Column(DECIMAL(5, 2), default=1.00)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC), onupdate=datetime.now(UTC))