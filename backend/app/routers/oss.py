from fastapi import APIRouter
import backend.app.utils.kobo_util as oss_util
from backend.app.schemas.oss_url import OssUrl

router = APIRouter()
@router.post("/")
async def get_key(key:str, response_model=OssUrl):
    url=oss_util.get_private_url(key)

    return OssUrl(url=url)