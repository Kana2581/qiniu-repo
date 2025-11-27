import uuid
from datetime import datetime, UTC

from sqlalchemy import Column, String, TIMESTAMP, Integer, Text, DECIMAL

from backend.app.core.database import Base


class Assistant(Base):
    __tablename__ = "assistant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    base_url = Column(String(255), nullable=True, comment='模型基础URL')
    provider = Column(String(100), nullable=False, comment='模型提供商')
    model_name = Column(String(100), nullable=False, comment='模型名称')
    api_key = Column(String(255), nullable=True, comment='API Key')

    description = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)  # 可以是 URL 或路径

    prompt_text = Column(Text,default="你是一个助手")
    window_size = Column(Integer, default=30)

    voice_type = Column(String(100), nullable=False, default='甜美教学小源')
    voice_name = Column(String(100),nullable=False,default='甜美教学小源')


    speed_ratio = Column(DECIMAL(5, 2), default=1.00)
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    system_type=Column(String(64),default="windows 10")
    base_file_path=Column(String(255), nullable=True)





