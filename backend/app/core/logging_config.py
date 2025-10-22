import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str = "app_logger") -> logging.Logger:
    """
    创建并返回一个配置好的日志记录器（Logger）。

    如果指定名称的 logger 尚未设置处理器（handlers），则：
    - 设置日志级别为 INFO；
    - 使用指定的格式化器同时将日志输出到文件和控制台；
    - 文件输出使用 RotatingFileHandler，实现日志文件的自动轮转（最大10MB，保留5个历史文件）。

    参数:
        name (str): 日志记录器的名称，默认为 "app_logger"。

    返回:
        logging.Logger: 配置好的日志记录器实例。
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        # 设置文件日志处理器，支持日志轮转（10MB一个文件，最多保留5个）
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5,encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 设置控制台日志处理器

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger