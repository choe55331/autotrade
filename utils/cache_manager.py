"""
utils/cache_manager.py
캐시 관리 시스템
"""

"""
API 호출 결과를 캐싱하여 성능 최적화
"""
import logging
import time
from typing import Any, Optional, Callable
from functools import wraps
from collections import OrderedDict
from threading import RLock

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Thread-safe LRU 캐시 관리자

    Features:
    - TTL (Time To Live) 지원
    - LRU (Least Recently Used) 정책
    - Thread-safe
    - 통계 수집 (hit rate)
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        """
        초기화

        Args:
            max_size: 최대 캐시 항목 수
            default_ttl: 기본 TTL (초)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl

        self._cache: OrderedDict = OrderedDict()
        self._timestamps: dict = {}
        self._lock = RLock()

        self._hits = 0
        self._misses = 0

        logger.info(f"CacheManager 초기화: max_size={max_size}, ttl={default_ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 값 또는 None (캐시 미스/만료)
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            if key in self._timestamps:
                if time.time() > self._timestamps[key]:
                    del self._cache[key]
                    del self._timestamps[key]
                    self._misses += 1
                    logger.debug(f"Cache expired: {key}")
                    return None

            self._cache.move_to_end(key)
            self._hits += 1

            value = self._cache[key]
            logger.debug(f"Cache hit: {key}")
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        캐시에 값 저장

        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: TTL (초), None이면 default_ttl 사용
        """
        with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            expiry_time = time.time() + ttl

            self._cache[key] = value
            self._cache.move_to_end(key)
            self._timestamps[key] = expiry_time

            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                if oldest_key in self._timestamps:
                    del self._timestamps[oldest_key]
                logger.debug(f"Cache evicted (LRU): {oldest_key}")

            logger.debug(f"Cache set: {key} (TTL={ttl}s)")

    def delete(self, key: str):
        """캐시 항목 삭제"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._timestamps:
                del self._timestamps[key]
            logger.debug(f"Cache deleted: {key}")

    def clear(self):
        """모든 캐시 삭제"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """캐시 통계 반환"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.2f}%"
            }

    def cleanup_expired(self):
        """만료된 항목 정리"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, expiry in self._timestamps.items()
                if current_time > expiry
            ]

            for key in expired_keys:
                del self._cache[key]
                del self._timestamps[key]

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired items")


_global_cache = None


def get_cache_manager() -> CacheManager:
    """전역 캐시 매니저 반환 (싱글톤)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager(max_size=1000, default_ttl=60)
    return _global_cache


def cached(ttl: int = 60, key_func: Optional[Callable] = None):
    """
    함수 결과를 캐싱하는 데코레이터

    Args:
        ttl: TTL (초)
        key_func: 커스텀 키 생성 함수 (args, kwargs를 받아 str 반환)

    Usage:
    """
        @cached(ttl=300)
        def expensive_function(arg1, arg2):
            return result

        @cached(ttl=60, key_func=lambda args, kwargs: f"custom_{args[0]}")
        def custom_key_function(stock_code):
            return result
    """
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            if key_func:
                cache_key = key_func(args, kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}"
                if args:
                    cache_key += f":{str(args)}"
                if kwargs:
                    cache_key += f":{str(sorted(kwargs.items()))}"

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)

            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


__all__ = [
    'CacheManager',
    'get_cache_manager',
    'cached',
]
