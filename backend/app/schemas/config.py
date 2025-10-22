# 请求体模型，只允许更新部分字段
from typing import Optional

from pydantic import BaseModel


class ConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    font_size: Optional[int] = None
    auto_save: Optional[bool] = None
    language: Optional[str] = None
    short_text_example: Optional[str] = None