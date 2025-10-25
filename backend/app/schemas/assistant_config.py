

from pydantic import BaseModel
from typing import Optional

class AssistantCreate(BaseModel):
    name: str
    base_url: str
    provider: str
    model_name: str
    api_key: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    prompt_text: Optional[str] = None
    window_size: Optional[int] = 30
    voice_name: Optional[str] = None
    voice_type: Optional[str] = None
    speech_speed: float = 1.0
    system_type: Optional[str] = None
    base_file_path: str = None




class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    prompt_text: Optional[str] = None
    window_size: Optional[int] = None
    voice_type: Optional[str] = None
    speech_speed: float = 1.0
    base_file_path: Optional[str] = None
    voice_name: Optional[str] = None
    system_type: Optional[str] = None

class AssistantResponse(BaseModel):
    id: int
    name: str
    base_url: str
    provider: str
    model_name: str
    api_key: str
    description: Optional[str]
    avatar: Optional[str]
    prompt_text: Optional[str]
    window_size: int
    voice_type: Optional[str] = None
    speech_speed: float = 1.0
    base_file_path: str = None
    voice_name: Optional[str] = None
    system_type: Optional[str] = None
    model_config = {
        "from_attributes": True
    }
