"""Redis cache module."""

from typing import Optional, Any
import json
from redis import Redis
from app.core.config import settings

class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = settings.CACHE_TTL
    ) -> bool:
        """Set value in cache with expiration."""
        try:
            return self.redis.setex(
                key,
                expire,
                json.dumps(value)
            )
        except Exception:
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
            
    async def clear(self) -> bool:
        """Clear all cache."""
        try:
            return bool(self.redis.flushdb())
        except Exception:
            return False

# Global cache instance
cache = RedisCache()
