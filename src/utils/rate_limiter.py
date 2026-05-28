import os
import json
import asyncio
import time
from typing import Optional

from fastapi import HTTPException

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def _redis_check(user_id: str, limit: int, window: int) -> Optional[bool]:
    try:
        import redis.asyncio as aioredis
    except Exception:
        return None

    try:
        client = aioredis.from_url(REDIS_URL)
        key = f"rl:admin:{user_id}"
        # Use INCR and EXPIRE atomically via pipeline
        async with client.pipeline() as pipe:
            await pipe.incr(key)
            await pipe.ttl(key)
            res = await pipe.execute()

        # res[0] is the counter, res[1] is ttl
        count = int(res[0])
        ttl = int(res[1]) if res[1] is not None else -1
        if ttl < 0:
            # set expiry
            await client.expire(key, window)

        await client.close()

        return count <= limit
    except Exception:
        return None


# Simple in-process fallback limiter
_local_lock = asyncio.Lock()
_local_store = {}

async def _local_check(user_id: str, limit: int, window: int) -> bool:
    now = time.time()
    async with _local_lock:
        entries = _local_store.get(user_id, [])
        entries = [t for t in entries if now - t < window]
        entries.append(now)
        _local_store[user_id] = entries
        return len(entries) <= limit


async def check_admin_rate_limit(user_id: str, limit: int = 3, window: int = 60) -> None:
    """Check rate limit for admin actions. Raises HTTPException(429) on limit exceed.
    Tries Redis first, falls back to in-process limiter if Redis not available."""
    redis_ok = await _redis_check(user_id, limit, window)
    if redis_ok is None:
        ok = await _local_check(user_id, limit, window)
    else:
        ok = redis_ok

    if not ok:
        raise HTTPException(status_code=429, detail="Too many requests")
