from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    content: str = Field( description="用户输入的消息内容")
    id: str= Field( description="前端生成的 UUID（前端唯一标识消息）")
    type:str