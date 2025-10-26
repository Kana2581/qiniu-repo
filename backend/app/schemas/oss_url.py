from pydantic import BaseModel


class OssUrl(BaseModel):
    url: str