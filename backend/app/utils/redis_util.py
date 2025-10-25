import asyncio
import uuid
from datetime import datetime, UTC
from typing import Optional
from fastapi import Request, HTTPException

from backend.app.core.connection import redis_client

LOCK_EXPIRE = 60  # 锁过期时间（秒）
# 限流配置
RATE_LIMIT = 5  # 每分钟最多 5 次
TIME_WINDOW = 60  # 单位：秒

def get_client_key(request: Request) -> str:
    # 可根据 IP、token 或 user_id 定义唯一 key
    client_ip = request.client.host
    return f"rate-limit:{client_ip}"

async def check_rate_limit(request: Request) -> bool:
    key = get_client_key(request)
    now = int(datetime.now(UTC).timestamp() // TIME_WINDOW)
    redis_key = f"{key}:{now}"

    current_count = await redis_client.get(redis_key)

    if current_count and int(current_count) >= RATE_LIMIT:
        return False  # 被限流
    async with redis_client.pipeline() as pipe:
        pipe.incr(redis_key)
        pipe.expire(redis_key, TIME_WINDOW)
        await pipe.execute()
    return True
def get_lock_key(session_id: str) -> str:
    return f"session-lock:{session_id}"

async def acquire_lock(session_id: str, expire: int = LOCK_EXPIRE) -> Optional[str]:
    """
    加锁：返回唯一锁标识（lock_value），失败返回 None
    """
    lock_key = get_lock_key(session_id)
    lock_value = str(uuid.uuid4())  # 给锁加一个唯一值防止误删
    is_locked = await redis_client.set(lock_key, lock_value, nx=True, ex=expire)
    return lock_value if is_locked else None



async def release_lock(session_id: str, lock_value: str) -> bool:
    lock_key = f"session-lock:{session_id}"
    lua_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    # 1 个 key，1 个 arg
    result = await redis_client.eval(lua_script, 1, lock_key, lock_value)
    return result == 1

async def publish_cancel(stream_id: str, reason: str):
    channel = f"stream-cancel-{stream_id}"
    await redis_client.publish(channel, reason)

# 监听端（流生成器包装器）
class StreamCancellation:
    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        self.cancelled = asyncio.Event()

    async def subscriber(self):
        channel = f"stream-cancel-{self.stream_id}"
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)

        async for message in pubsub.listen():
            if message["type"] == "message":
                print(f"Stream {self.stream_id} cancelled due to: {message['data']}")
                self.cancelled.set()
                break

    def is_cancelled(self) -> bool:
        return self.cancelled.is_set()