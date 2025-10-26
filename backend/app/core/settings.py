from typing import List, Annotated

from pydantic import Field, validator, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    对应.env配置文件
    """
    #MySQL数据库url
    DATABASE_URL: str

    #是否开启网络代理
    HTTP_PROXY: str | None = None
    #是否开启网络代理
    HTTPS_PROXY: str | None = None

    #redis 地址
    REDIS_HOST:str
    #redis 端口
    REDIS_PORT: int
    #redis 密码
    REDIS_PASSWORD :str
    REDIS_DECODE_RESPONSES : bool

    HISTORY_MAX_TOKENS:int=5000

    DEV:bool=True
    TTS_AND_ASR_API_KEY:str

    KOBO_ACCESS_KEY:str
    KOBO_SECRET_KEY:str
    KOBO_BUCKET_NAME:str
    KOBO_BUCKET_DOMAIN:str
    class Config:
        env_file = ".env"

settings = Settings()