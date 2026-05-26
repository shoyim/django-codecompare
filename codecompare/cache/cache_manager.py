"""Redis-backed cache manager with gzip compression."""
from __future__ import annotations
import gzip
import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

_COMPRESS_THRESHOLD = 1024  # bytes


def _make_key(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"codecompare:{prefix}:{digest}"


def _serialise(value: Any) -> bytes:
    raw = json.dumps(value, default=str).encode()
    if len(raw) > _COMPRESS_THRESHOLD:
        return b"\x01" + gzip.compress(raw, compresslevel=6)
    return b"\x00" + raw


def _deserialise(data: bytes) -> Any:
    flag, payload = data[0:1], data[1:]
    if flag == b"\x01":
        return json.loads(gzip.decompress(payload))
    return json.loads(payload)


class CacheManager:
    def __init__(self, backend: str = "default", default_ttl: int = 3600):
        self._backend = backend
        self._ttl = default_ttl
        self._cache: Any = None

    def _get_cache(self):
        if self._cache is None:
            try:
                from django.core.cache import caches
                self._cache = caches[self._backend]
            except Exception:
                self._cache = _NullCache()
        return self._cache

    def get(self, key: str) -> Any | None:
        try:
            raw = self._get_cache().get(key)
            if raw is None:
                return None
            return _deserialise(raw)
        except Exception as exc:
            logger.warning("Cache get error for %s: %s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        try:
            self._get_cache().set(key, _serialise(value), timeout=ttl or self._ttl)
        except Exception as exc:
            logger.warning("Cache set error for %s: %s", key, exc)

    def delete(self, key: str) -> None:
        try:
            self._get_cache().delete(key)
        except Exception as exc:
            logger.warning("Cache delete error for %s: %s", key, exc)

    def comparison_key(self, old_code: str, new_code: str, language: str) -> str:
        return _make_key("comparison", old_code, new_code, language)

    def get_comparison(self, old_code: str, new_code: str, language: str) -> Any | None:
        return self.get(self.comparison_key(old_code, new_code, language))

    def set_comparison(self, old_code: str, new_code: str, language: str, result: Any) -> None:
        self.set(self.comparison_key(old_code, new_code, language), result)


class _NullCache:
    def get(self, key: str) -> None:
        return None

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        pass

    def delete(self, key: str) -> None:
        pass


_default_cache = CacheManager()


def get_cache() -> CacheManager:
    return _default_cache
