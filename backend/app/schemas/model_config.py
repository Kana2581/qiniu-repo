from typing import Optional

from pydantic import BaseModel


class ModelConfig(BaseModel):
    prompt_text: str
    model_name: str
    provider: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_config = {
        "from_attributes": True
    }