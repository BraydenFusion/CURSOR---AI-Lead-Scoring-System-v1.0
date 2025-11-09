"""Per-API-key rate limiting utilities."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from threading import RLock
from typing import Deque, Dict, List, Optional, Tuple

from redis import Redis

from ..config import get_settings

settings = get_settings()

WINDOW_SECONDS = 3600
MAX_HISTORY = 50


@dataclass
class RateLimitStatus:
    limit: int
    remaining: int
    reset_epoch: int


class RateLimiter:
    """Simple per-key rate limiter with optional Redis backend."""

    def __init__(self) -> None:
        self._redis: Optional[Redis] = self._initialize_redis()
        self._memory_counters: Dict[str, Tuple[int, float]] = {}
        self._history: Dict[str, Deque[Tuple[int, int]]] = {}
        self._lock = RLock()

    def _initialize_redis(self) -> Optional[Redis]:
        try:
            client = Redis.from_url(settings.redis_url, decode_responses=True)
            # Test connection (non-fatal)
            client.ping()
            return client
        except Exception:
            return None

    def _redis_key(self, key: str) -> str:
        return f"api_rate:{key}"

    def check(self, key: str, limit: int) -> RateLimitStatus:
        now = int(time.time())
        reset_epoch = now + WINDOW_SECONDS

        if limit <= 0:
            return RateLimitStatus(limit=limit, remaining=limit, reset_epoch=reset_epoch)

        if self._redis:
            redis_key = self._redis_key(key)
            try:
                pipeline = self._redis.pipeline()
                pipeline.incr(redis_key)
                pipeline.ttl(redis_key)
                current, ttl = pipeline.execute()
                if current == 1:
                    self._redis.expire(redis_key, WINDOW_SECONDS)
                reset_epoch = now + (ttl if ttl and ttl > 0 else WINDOW_SECONDS)
                remaining = max(limit - current, 0)
                if current > limit:
                    raise RateLimitExceeded(limit=limit, remaining=0, reset_epoch=reset_epoch)
                self._append_history(key, timestamp=now, count=current)
                return RateLimitStatus(limit=limit, remaining=remaining, reset_epoch=reset_epoch)
            except RateLimitExceeded:
                raise
            except Exception:
                # Fallback to memory if Redis fails unexpectedly
                pass

        with self._lock:
            count, expiry = self._memory_counters.get(key, (0, float(now + WINDOW_SECONDS)))
            if expiry <= now:
                count = 0
                expiry = float(now + WINDOW_SECONDS)
            count += 1
            self._memory_counters[key] = (count, expiry)
            remaining = max(limit - count, 0)
            reset_epoch = int(expiry)
            self._append_history(key, timestamp=now, count=count)
            if count > limit:
                raise RateLimitExceeded(limit=limit, remaining=0, reset_epoch=reset_epoch)
            return RateLimitStatus(limit=limit, remaining=remaining, reset_epoch=reset_epoch)

    def peek(self, key: str, limit: int) -> RateLimitStatus:
        now = int(time.time())
        if limit <= 0:
            return RateLimitStatus(limit=limit, remaining=limit, reset_epoch=now + WINDOW_SECONDS)

        if self._redis:
            redis_key = self._redis_key(key)
            try:
                value = self._redis.get(redis_key)
                current = int(value) if value else 0
                ttl = self._redis.ttl(redis_key)
                reset_epoch = now + (ttl if ttl and ttl > 0 else WINDOW_SECONDS)
                remaining = max(limit - current, 0)
                return RateLimitStatus(limit=limit, remaining=remaining, reset_epoch=reset_epoch)
            except Exception:
                pass

        with self._lock:
            count, expiry = self._memory_counters.get(key, (0, float(now + WINDOW_SECONDS)))
            if expiry <= now:
                count = 0
                expiry = float(now + WINDOW_SECONDS)
            remaining = max(limit - count, 0)
            return RateLimitStatus(limit=limit, remaining=remaining, reset_epoch=int(expiry))

    def history(self, key: str) -> List[Tuple[int, int]]:
        with self._lock:
            if key not in self._history:
                return []
            return list(self._history[key])

    def _append_history(self, key: str, *, timestamp: int, count: int) -> None:
        with self._lock:
            if key not in self._history:
                self._history[key] = deque(maxlen=MAX_HISTORY)
            self._history[key].append((timestamp, count))


class RateLimitExceeded(Exception):
    """Raised when the rate limit has been exceeded."""

    def __init__(self, *, limit: int, remaining: int, reset_epoch: int) -> None:
        self.limit = limit
        self.remaining = remaining
        self.reset_epoch = reset_epoch
        super().__init__("Rate limit exceeded")


rate_limiter = RateLimiter()

