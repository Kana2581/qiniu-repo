from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

import backend.app.utils.kobo_util as oss_util
from backend.app.schemas.oss_url import OssUrl

router = APIRouter()
@router.get("/", response_model=OssUrl)
@cache(expire=3600)
async def get_key(key: str = Query(...)):
    url = oss_util.get_private_url(key)
    return OssUrl(url=url)