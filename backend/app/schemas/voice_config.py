from typing import Optional

from pydantic import BaseModel


class VoiceConfigBase(BaseModel):
    voice_type: Optional[str] = None
    speed_ratio:  Optional[float] = 1.0
    model_config = {
        "from_attributes": True
    }