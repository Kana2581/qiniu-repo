from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, TIMESTAMP

from backend.app.core.database import Base


class ModelConfig(Base):
    __tablename__ = "model_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_url = Column(String(255), nullable=False, comment='模型基础URL')
    provider = Column(String(100), nullable=False, comment='模型提供商')
    model_name = Column(String(100), nullable=False, comment='模型名称')
    api_key = Column(String(255), nullable=False, comment='API Key')
    created_at = Column(TIMESTAMP, default=datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=datetime.now(UTC), onupdate=datetime.now(UTC))