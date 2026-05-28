# src/services/cache_service.py
import asyncio
import json
import hashlib
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_client=None):
        # In production, this would use Redis client
        self.cache = {}
        self.default_ttl = 300  # 5 minutes
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if entry['expires_at'] > datetime.now():
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
            
            self.cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            
            logger.debug(f"Cache set for key: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache deleted for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if key in self.cache:
            if self.cache[key]['expires_at'] > datetime.now():
                return True
            else:
                await self.delete(key)
        return False
    
    async def clear_expired(self) -> int:
        """Clear expired cache entries and return count cleared"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        now = datetime.now()
        
        expired_entries = len([
            key for key, entry in self.cache.items()
            if entry['expires_at'] <= now
        ])
        
        active_entries = total_entries - expired_entries
        
        # Calculate memory usage (approximate)
        memory_usage = sum(
            len(str(entry)) + len(key) 
            for key, entry in self.cache.items()
        )
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'memory_usage_bytes': memory_usage,
            'hit_rate': await self.calculate_hit_rate()
        }
    
    async def calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # In production, this would track actual hits/misses
        # For demo, return a mock value
        return 0.85
    
    def generate_cache_key(self, func, *args, **kwargs) -> str:
        """Generate cache key from function and arguments"""
        key_parts = [func.__module__, func.__name__]
        
        # Add args to key
        for arg in args:
            key_parts.append(str(arg))
        
        # Add kwargs to key
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        # Create hash
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cached(self, ttl: Optional[int] = None, key_func: Optional[callable] = None):
        """Decorator for caching function results"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.generate_cache_key(func, *args, **kwargs)
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    async def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        results = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        return results
    
    async def batch_set(self, key_value_pairs: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        try:
            for key, value in key_value_pairs.items():
                await self.set(key, value, ttl)
            return True
        except Exception as e:
            logger.error(f"Batch set failed: {e}")
            return False
    
    async def get_or_set(self, key: str, default_func: callable, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using default function"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Execute default function to get value
        if asyncio.iscoroutinefunction(default_func):
            value = await default_func()
        else:
            value = default_func()
        
        # Set value in cache
        await self.set(key, value, ttl)
        return value
