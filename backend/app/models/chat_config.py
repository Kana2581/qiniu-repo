from datetime import datetime, UTC

from sqlalchemy import Column, Integer, Text, TIMESTAMP

from backend.app.core.database import Base


class ChatConfig(Base):
    __tablename__ = "chat_config"

    id = Column(Integer, primary_key=True, autoincrement=True)

    prompt_text = Column(Text)
    window_size = Column(Integer, default=30)



    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC), onupdate=datetime.now(UTC))

