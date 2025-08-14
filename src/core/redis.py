import redis.asyncio as redis
from .config import settings
from .logger import logger


class RedisManager:
    """Redis connection manager"""
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._connection = None
    
    async def get_connection(self):
        """Get Redis connection"""
        if not self._connection:
            try:
                self._connection = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._connection.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return self._connection
    
    async def close(self):
        """Close Redis connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None


redis_manager = RedisManager()
