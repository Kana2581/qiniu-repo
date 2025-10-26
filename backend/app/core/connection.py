import redis.asyncio as redis
from minio import Minio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.app.core.settings import settings

# SQLAlchemy

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,password=settings.REDIS_PASSWORD,decode_responses=settings.REDIS_DECODE_RESPONSES)

