"""
Performance monitoring and optimization utilities.
"""
import time
import asyncio
import functools
import json
import hashlib
from typing import Any, Callable, Dict, Optional, Union
from contextlib import asynccontextmanager
import logging
import redis.asyncio as redis
from ..core.config import settings

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track application performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.redis_client = None
    
    async def init_redis(self):
        """Initialize Redis connection for metrics storage"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Could not connect to Redis for metrics: {e}")
            self.redis_client = None
    
    @asynccontextmanager
    async def track_operation(self, operation_name: str, metadata: Dict[str, Any] = None):
        """Context manager to track operation performance"""
        start_time = time.time()
        error = None
        
        try:
            yield
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            await self._record_metric(operation_name, duration, error, metadata or {})
    
    async def _record_metric(self, operation: str, duration: float, error: Optional[str], metadata: Dict[str, Any]):
        """Record performance metric"""
        metric = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "error": error,
            "timestamp": time.time(),
            "metadata": metadata
        }
        
        # Store in memory
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append(metric)
        
        # Keep only last 100 metrics per operation in memory
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
        
        # Store in Redis if available
        if self.redis_client:
            try:
                key = f"metrics:{operation}"
                await self.redis_client.lpush(key, json.dumps(metric))
                await self.redis_client.ltrim(key, 0, 999)  # Keep last 1000 metrics
                await self.redis_client.expire(key, 86400)  # Expire after 24 hours
            except Exception as e:
                logger.warning(f"Could not store metric in Redis: {e}")
    
    def get_metrics_summary(self, operation: str = None) -> Dict[str, Any]:
        """Get performance metrics summary"""
        if operation:
            metrics = self.metrics.get(operation, [])
            operations = {operation: metrics}
        else:
            operations = self.metrics
        
        summary = {}
        
        for op_name, op_metrics in operations.items():
            if not op_metrics:
                continue
            
            durations = [m["duration_ms"] for m in op_metrics if not m["error"]]
            errors = [m for m in op_metrics if m["error"]]
            
            if durations:
                summary[op_name] = {
                    "total_calls": len(op_metrics),
                    "successful_calls": len(durations),
                    "error_count": len(errors),
                    "error_rate_percent": round((len(errors) / len(op_metrics)) * 100, 2),
                    "avg_duration_ms": round(sum(durations) / len(durations), 2),
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "last_24h": len([m for m in op_metrics if time.time() - m["timestamp"] < 86400])
                }
            else:
                summary[op_name] = {
                    "total_calls": len(op_metrics),
                    "successful_calls": 0,
                    "error_count": len(errors),
                    "error_rate_percent": 100.0,
                    "last_24h": len([m for m in op_metrics if time.time() - m["timestamp"] < 86400])
                }
        
        return summary


class CacheManager:
    """Advanced caching system with Redis backend"""
    
    def __init__(self):
        self.redis_client = None
        self.local_cache = {}
        self.local_cache_ttl = {}
    
    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Redis for caching: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key from arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            # Try Redis first
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fall back to local cache
            if key in self.local_cache:
                if key in self.local_cache_ttl and time.time() > self.local_cache_ttl[key]:
                    del self.local_cache[key]
                    del self.local_cache_ttl[key]
                else:
                    return self.local_cache[key]
            
            return default
            
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or settings.CACHE_TTL_SECONDS
            
            # Try Redis first
            if self.redis_client:
                await self.redis_client.setex(key, ttl, json.dumps(value, default=str))
                return True
            
            # Fall back to local cache
            self.local_cache[key] = value
            self.local_cache_ttl[key] = time.time() + ttl
            
            # Clean up expired local cache entries periodically
            if len(self.local_cache) > 1000:
                await self._cleanup_local_cache()
            
            return True
            
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            # Try Redis first
            if self.redis_client:
                await self.redis_client.delete(key)
            
            # Clean local cache
            if key in self.local_cache:
                del self.local_cache[key]
            if key in self.local_cache_ttl:
                del self.local_cache_ttl[key]
            
            return True
            
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def _cleanup_local_cache(self):
        """Clean up expired entries from local cache"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.local_cache_ttl.items()
            if current_time > expiry
        ]
        
        for key in expired_keys:
            del self.local_cache[key]
            del self.local_cache_ttl[key]


# Global instances
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()


def track_performance(operation_name: str = None, include_args: bool = False):
    """Decorator to track function performance"""
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                metadata = {}
                if include_args:
                    metadata["args_count"] = len(args)
                    metadata["kwargs_keys"] = list(kwargs.keys())
                
                async with performance_monitor.track_operation(op_name, metadata):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                metadata = {}
                if include_args:
                    metadata["args_count"] = len(args)
                    metadata["kwargs_keys"] = list(kwargs.keys())
                
                # For sync functions, we need to handle this differently
                start_time = time.time()
                error = None
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    error = str(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    # Note: This will be sync, so metrics might not be stored in Redis immediately
                    asyncio.create_task(
                        performance_monitor._record_metric(op_name, duration, error, metadata)
                    )
            
            return sync_wrapper
    return decorator


def cached(ttl: int = None, key_prefix: str = None, include_args: bool = True):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or f"cache:{func.__module__}.{func.__name__}"
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if include_args:
                    cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)
                else:
                    cache_key = prefix
                
                # Try to get from cache
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await cache_manager.set(cache_key, result, ttl)
                return result
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if include_args:
                    cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)
                else:
                    cache_key = prefix
                
                # For sync functions, we'll need to handle caching differently
                # This is a simplified version - in practice, you might want to use a sync cache
                result = func(*args, **kwargs)
                
                # Store in cache asynchronously
                asyncio.create_task(cache_manager.set(cache_key, result, ttl))
                return result
            
            return sync_wrapper
    
    return decorator


async def init_performance_utils():
    """Initialize performance monitoring and caching utilities"""
    await performance_monitor.init_redis()
    await cache_manager.init_redis()
    logger.info("Performance utilities initialized")


def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics"""
    return performance_monitor.get_metrics_summary()


async def clear_cache(pattern: str = None):
    """Clear cache entries matching pattern"""
    if pattern and cache_manager.redis_client:
        try:
            keys = await cache_manager.redis_client.keys(pattern)
            if keys:
                await cache_manager.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries matching pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
    else:
        # Clear local cache
        cache_manager.local_cache.clear()
        cache_manager.local_cache_ttl.clear()
        logger.info("Cleared local cache")