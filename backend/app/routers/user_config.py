from typing import Optional, Dict

from fastapi import APIRouter, HTTPException

from backend.app.schemas.config import ConfigUpdate
from backend.app.utils.json_util import JSONConfig

router = APIRouter()
config = JSONConfig("config.json")





@router.get("/config")
def get_config():
    """获取当前配置"""
    return config.all()


@router.put("/config")
def update_config(updates: ConfigUpdate):
    """更新配置"""
    update_data: Dict[str, any] = {k: v for k, v in updates.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供可更新的字段")

    try:
        config.update(update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "配置更新成功", "config": config.all()}