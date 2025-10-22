import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError, Field

# 定义配置模型，必填字段加 Field(..., description="") 表示不能为空
class ConfigModel(BaseModel):
    system_prompt: str = Field(..., description="系统提示词，不能为空")
    theme: str = "light"
    notifications_enabled: bool = True
    font_size: int = 12
    auto_save: bool = False
    language: str = "en"
    short_text_example: str = ""

class JSONConfig:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.config: Optional[ConfigModel] = None
        self.load()

    def load(self):
        """读取 JSON 文件并验证，如果文件不存在或为空，生成默认配置"""
        if self.file_path.exists():
            try:
                content = self.file_path.read_text(encoding="utf-8").strip()
                if content:  # 文件非空
                    data = json.loads(content)
                    self.config = ConfigModel(**data)
                else:
                    self._create_default()
            except (json.JSONDecodeError, ValidationError) as e:
                raise ValueError(f"JSON 配置文件错误: {e}")
        else:
            self._create_default()

    def _create_default(self):
        """创建默认配置并保存"""
        self.config = ConfigModel( system_prompt="你是一个助手")
        self.save()

    def save(self):
        """保存当前配置到 JSON 文件"""
        if self.config:
            self.file_path.write_text(
                self.config.model_dump_json(indent=4, ensure_ascii=False),
                encoding="utf-8"
            )

    def update(self, updates: Dict[str, Any]):
        """更新指定字段，验证必填字段"""
        if not self.config:
            raise ValueError("配置未加载")
        data = self.config.dict()
        for key, value in updates.items():
            if key in data:
                data[key] = value
        try:
            self.config = ConfigModel(**data)
        except ValidationError as e:
            raise ValueError(f"更新失败，必填字段缺失或类型错误: {e}")
        self.save()

    def get(self, key: str) -> Any:
        if not self.config:
            raise ValueError("配置未加载")
        return getattr(self.config, key, None)

    def all(self) -> Dict[str, Any]:
        if not self.config:
            raise ValueError("配置未加载")
        return self.config.dict()


