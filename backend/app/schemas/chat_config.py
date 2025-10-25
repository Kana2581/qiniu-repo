from typing import Optional

from pydantic import BaseModel, Field


class ChatConfigBase(BaseModel):
    model_id: int
    prompt_text: Optional[str] = None
    window_size: int = Field(default=30)