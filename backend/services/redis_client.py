import redis.asyncio as redis
import json
import os
from typing import Optional, Any
from datetime import timedelta, datetime

class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
        self.client: Optional[redis.Redis] = None
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            print("Redis connection established")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
    
    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            if self.client:
                await self.client.ping()
                return True
        except:
            pass
        return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Redis get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        if not self.client:
            return False
        
        try:
            value_str = json.dumps(value)
            if expire:
                await self.client.setex(key, expire, value_str)
            else:
                await self.client.set(key, value_str)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.client:
            return False
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    async def get_cached_valuation(self, property_hash: str) -> Optional[dict]:
        """Get cached property valuation"""
        cache_key = f"valuation:{property_hash}"
        return await self.get(cache_key)
    
    async def cache_valuation(self, property_hash: str, valuation: dict, ttl: int = 3600) -> bool:
        """Cache property valuation with TTL"""
        cache_key = f"valuation:{property_hash}"
        return await self.set(cache_key, valuation, expire=ttl)
    
    async def increment(self, key: str) -> int:
        """Increment a counter"""
        if not self.client:
            return 0
        
        try:
            return await self.client.incr(key)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0
    
    async def track_api_call(self, endpoint: str, user_id: Optional[str] = None):
        """Track API usage"""
        if not self.client:
            return
        
        try:
            # Daily counter
            today_key = f"api:calls:{endpoint}:{datetime.now().strftime('%Y%m%d')}"
            await self.increment(today_key)
            
            # Total requests counter
            total_key = "api:total_requests"
            await self.increment(total_key)
            
            # User-specific counter if user_id provided
            if user_id:
                user_key = f"api:user:{user_id}:{datetime.now().strftime('%Y%m%d')}"
                await self.increment(user_key)
        except Exception as e:
            print(f"Redis tracking error: {e}")
    
    async def get_api_stats(self) -> Optional[dict]:
        """Get API usage statistics"""
        if not self.client:
            return None
        
        try:
            # Get total requests
            total_requests = await self.client.get("api:total_requests")
            total_requests = int(total_requests) if total_requests else 0
            
            # Get today's requests
            today_key = f"api:daily:{datetime.now().strftime('%Y%m%d')}"
            daily_requests = await self.client.get(today_key)
            daily_requests = int(daily_requests) if daily_requests else 0
            
            # Simplified average response time (would be calculated properly in production)
            avg_response_time = 45.0 + (total_requests % 50) / 10  # Mock calculation
            
            return {
                "total_requests": total_requests,
                "daily_requests": daily_requests,
                "avg_response_time": avg_response_time
            }
        except Exception as e:
            print(f"Redis get_api_stats error: {e}")
            return None

redis_client = RedisClient()