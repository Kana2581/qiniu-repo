from pydantic import BaseModel
from datetime import datetime

class SessionAssistantBase(BaseModel):
    assistant_id: int

class SessionAssistantCreate(SessionAssistantBase):
    pass

class SessionAssistantUpdate(SessionAssistantBase):
    pass

class SessionAssistantOut(SessionAssistantBase):
    session_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }