from typing import Optional

from pydantic import BaseModel


class VoiceConfigBase(BaseModel):
    voice_type: Optional[str] = None
    speech_speed: float = 1.0