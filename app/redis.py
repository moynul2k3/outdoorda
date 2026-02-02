from redis.asyncio import Redis
redis_client: Redis | None = None
from app.config import settings

REDIS_URL: str = settings.REDIS_URL

def init_redis():
    global redis_client
    print("Initializing Redis connection...", REDIS_URL)
    if not redis_client:
        redis_client = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return redis_client

def get_redis() -> Redis:
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    return redis_client
