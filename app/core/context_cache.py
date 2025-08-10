"""
Context caching utilities for content generation
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import redis
import pickle
import logging

logger = logging.getLogger(__name__)

# Try to connect to Redis
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=False)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")

# In-memory cache fallback
_memory_cache: Dict[str, tuple[Any, datetime]] = {}
CACHE_TTL = timedelta(hours=2)

def _get_cache_key(key_parts: list) -> str:
    """Generate a cache key from parts"""
    key_string = "|".join(str(part) for part in key_parts)
    return f"ada:context:{hashlib.md5(key_string.encode()).hexdigest()}"

def get_cached_context(key_parts: list) -> Optional[Dict[str, Any]]:
    """Get context from cache"""
    cache_key = _get_cache_key(key_parts)
    
    # Try Redis first
    if REDIS_AVAILABLE:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
    
    # Fallback to memory cache
    if cache_key in _memory_cache:
        value, timestamp = _memory_cache[cache_key]
        if datetime.utcnow() - timestamp < CACHE_TTL:
            return value
        else:
            del _memory_cache[cache_key]
    
    return None

def set_cached_context(key_parts: list, context: Dict[str, Any], ttl_hours: int = 2) -> None:
    """Set context in cache"""
    cache_key = _get_cache_key(key_parts)
    
    # Try Redis first
    if REDIS_AVAILABLE:
        try:
            redis_client.setex(
                cache_key,
                timedelta(hours=ttl_hours),
                pickle.dumps(context)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    # Always set in memory cache as fallback
    _memory_cache[cache_key] = (context, datetime.utcnow())
    
    # Clean old entries from memory cache
    if len(_memory_cache) > 100:
        now = datetime.utcnow()
        expired_keys = [
            k for k, (_, ts) in _memory_cache.items()
            if now - ts > CACHE_TTL
        ]
        for k in expired_keys:
            del _memory_cache[k]

def clear_context_cache(pattern: Optional[str] = None) -> None:
    """Clear context cache"""
    if REDIS_AVAILABLE and pattern:
        try:
            for key in redis_client.scan_iter(f"ada:context:{pattern}*"):
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    # Clear memory cache
    if pattern:
        keys_to_delete = [k for k in _memory_cache.keys() if pattern in k]
        for k in keys_to_delete:
            del _memory_cache[k]
    else:
        _memory_cache.clear()

@lru_cache(maxsize=128)
def get_cached_prompt_template(prompt_name: str, prompt_template: str) -> str:
    """Cache compiled prompt templates"""
    return prompt_template

def invalidate_prompt_cache():
    """Invalidate prompt template cache"""
    get_cached_prompt_template.cache_clear()