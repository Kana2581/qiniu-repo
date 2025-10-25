from fastapi import APIRouter
import backend.app.utils.kobo_util as oss_util
router = APIRouter()
@router.post("/")
async def get_key(key:str):
    return {"url":oss_util.get_private_url(key)}