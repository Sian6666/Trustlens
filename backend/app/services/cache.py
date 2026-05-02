import json
import time

import redis
from flask import current_app


class TTLMemoryCache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        entry = self._store.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key, value, ttl=60):
        self._store[key] = (time.time() + ttl, value)

    def delete_prefix(self, prefix):
        for key in list(self._store):
            if key.startswith(prefix):
                self._store.pop(key, None)


memory_cache = TTLMemoryCache()


def _redis_client():
    redis_url = current_app.config.get("REDIS_URL")
    if not redis_url:
        return None
    try:
        return redis.from_url(redis_url, decode_responses=True)
    except redis.RedisError:
        current_app.logger.warning("Redis unavailable, falling back to memory cache")
        return None


def get_json(key):
    client = _redis_client()
    if client:
        try:
            value = client.get(key)
            return json.loads(value) if value else None
        except redis.RedisError:
            current_app.logger.warning("Redis get failed for %s", key)
    return memory_cache.get(key)


def set_json(key, value, ttl=60):
    client = _redis_client()
    if client:
        try:
            client.setex(key, ttl, json.dumps(value))
            return
        except redis.RedisError:
            current_app.logger.warning("Redis set failed for %s", key)
    memory_cache.set(key, value, ttl)


def invalidate_prefix(prefix):
    client = _redis_client()
    if client:
        try:
            for key in client.scan_iter(f"{prefix}*"):
                client.delete(key)
            return
        except redis.RedisError:
            current_app.logger.warning("Redis invalidation failed for %s", prefix)
    memory_cache.delete_prefix(prefix)
