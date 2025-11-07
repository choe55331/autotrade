"""
Advanced Data Caching System - v5.12
Multi-level caching with LRU, TTL, and intelligent invalidation
"""
from dataclasses import dataclass
from typing import Any, Optional, Dict, Callable, List
from datetime import datetime, timedelta
from collections import OrderedDict
from threading import RLock
import json
import hashlib
import pickle
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """캐시 엔트리"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int
    last_accessed: datetime
    size_bytes: int
    tags: List[str]


@dataclass
class CacheStats:
    """캐시 통계"""
    total_hits: int
    total_misses: int
    total_sets: int
    total_deletes: int
    total_evictions: int
    hit_rate: float
    memory_usage_bytes: int
    entry_count: int
    uptime_seconds: float


class LRUCache:
    """
    LRU (Least Recently Used) Cache
    Thread-safe, TTL-aware caching with size limits
    """

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100,
                 default_ttl_seconds: int = 300):
        Args:
            max_size: 최대 엔트리 수
            max_memory_mb: 최대 메모리 사용량 (MB)
            default_ttl_seconds: 기본 TTL (초)
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl_seconds = default_ttl_seconds

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = RLock()

        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._deletes = 0
        self._evictions = 0
        self._start_time = datetime.now()
        self._current_memory_bytes = 0

        logger.info(f"LRU Cache initialized: max_size={max_size}, "
                   f"max_memory={max_memory_mb}MB, ttl={default_ttl_seconds}s")

    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 값 or None
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None

            entry = self._cache[key]

            if entry.expires_at and datetime.now() >= entry.expires_at:
                logger.debug(f"Cache EXPIRED: {key}")
                self._delete_entry(key)
                self._misses += 1
                return None

            entry.hit_count += 1
            entry.last_accessed = datetime.now()

            self._cache.move_to_end(key)

            self._hits += 1
            logger.debug(f"Cache HIT: {key} (hits={entry.hit_count})")

            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None,
            tags: Optional[List[str]] = None) -> bool:
        캐시에 값 저장

        Args:
            key: 캐시 키
            value: 저장할 값
            ttl_seconds: TTL (초), None이면 default TTL 사용
            tags: 태그 목록 (invalidation용)

        Returns:
            bool: 성공 여부
        with self._lock:
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception as e:
                logger.warning(f"Cannot pickle value for {key}: {e}")
                size_bytes = 1024

            if size_bytes > self.max_memory_bytes:
                logger.warning(f"Entry too large for cache: {key} ({size_bytes} bytes)")
                return False

            if key in self._cache:
                self._delete_entry(key)

            self._evict_if_needed(size_bytes)

            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                hit_count=0,
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                tags=tags or []
            )

            self._cache[key] = entry
            self._current_memory_bytes += size_bytes
            self._sets += 1

            logger.debug(f"Cache SET: {key} (size={size_bytes}, ttl={ttl}s, "
                        f"memory={self._current_memory_bytes/1024/1024:.1f}MB)")

            return True

    def delete(self, key: str) -> bool:
        """
        캐시 엔트리 삭제

        Args:
            key: 캐시 키

        Returns:
            bool: 삭제 성공 여부
        """
        with self._lock:
            if key in self._cache:
                self._delete_entry(key)
                self._deletes += 1
                logger.debug(f"Cache DELETE: {key}")
                return True
            return False

    def invalidate_by_tag(self, tag: str) -> int:
        """
        태그로 캐시 무효화

        Args:
            tag: 태그

        Returns:
            int: 삭제된 엔트리 수
        """
        with self._lock:
            keys_to_delete = [
                key for key, entry in self._cache.items()
                if tag in entry.tags
            ]

            for key in keys_to_delete:
                self._delete_entry(key)

            logger.info(f"Invalidated {len(keys_to_delete)} entries with tag '{tag}'")
            return len(keys_to_delete)

    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._current_memory_bytes = 0
            logger.info(f"Cache cleared: {count} entries deleted")

    def get_stats(self) -> CacheStats:
        """캐시 통계 조회"""
        with self._lock:
            total_ops = self._hits + self._misses
            hit_rate = self._hits / total_ops if total_ops > 0 else 0.0

            uptime = (datetime.now() - self._start_time).total_seconds()

            return CacheStats(
                total_hits=self._hits,
                total_misses=self._misses,
                total_sets=self._sets,
                total_deletes=self._deletes,
                total_evictions=self._evictions,
                hit_rate=hit_rate,
                memory_usage_bytes=self._current_memory_bytes,
                entry_count=len(self._cache),
                uptime_seconds=uptime
            )

    def _delete_entry(self, key: str) -> None:
        """엔트리 삭제 (internal)"""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_memory_bytes -= entry.size_bytes

    def _evict_if_needed(self, incoming_size: int) -> None:
        """필요시 오래된 엔트리 제거"""
        while (self._current_memory_bytes + incoming_size > self.max_memory_bytes and
               len(self._cache) > 0):
            oldest_key = next(iter(self._cache))
            logger.debug(f"Evicting by memory: {oldest_key}")
            self._delete_entry(oldest_key)
            self._evictions += 1

        while len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            logger.debug(f"Evicting by count: {oldest_key}")
            self._delete_entry(oldest_key)
            self._evictions += 1

    def cleanup_expired(self) -> int:
        """만료된 엔트리 정리"""
        with self._lock:
            now = datetime.now()
            keys_to_delete = [
                key for key, entry in self._cache.items()
                if entry.expires_at and entry.expires_at <= now
            ]

            for key in keys_to_delete:
                self._delete_entry(key)

            if keys_to_delete:
                logger.info(f"Cleaned up {len(keys_to_delete)} expired entries")

            return len(keys_to_delete)


class MultiLevelCache:
    """
    다단계 캐시
    L1 (Memory) -> L2 (Disk) 계층 구조
    """

    def __init__(self, l1_max_size: int = 1000, l1_max_memory_mb: int = 100,
                 l2_enabled: bool = True, l2_cache_dir: str = "data/cache"):
        Args:
            l1_max_size: L1 캐시 최대 크기
            l1_max_memory_mb: L1 캐시 최대 메모리
            l2_enabled: L2 (디스크) 캐시 활성화
            l2_cache_dir: L2 캐시 디렉토리
        self.l1_cache = LRUCache(
            max_size=l1_max_size,
            max_memory_mb=l1_max_memory_mb,
            default_ttl_seconds=300
        )

        self.l2_enabled = l2_enabled
        self.l2_cache_dir = Path(l2_cache_dir)

        if self.l2_enabled:
            self.l2_cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"L2 cache enabled: {self.l2_cache_dir}")

        self._lock = RLock()

        logger.info("Multi-level cache initialized")

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 조회 (L1 -> L2)"""
        value = self.l1_cache.get(key)
        if value is not None:
            logger.debug(f"L1 cache hit: {key}")
            return value

        if self.l2_enabled:
            value = self._get_from_l2(key)
            if value is not None:
                logger.debug(f"L2 cache hit: {key}")
                self.l1_cache.set(key, value)
                return value

        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None,
            tags: Optional[List[str]] = None, persist_l2: bool = True) -> bool:
        success = self.l1_cache.set(key, value, ttl_seconds, tags)

        if self.l2_enabled and persist_l2:
            self._set_to_l2(key, value, ttl_seconds)

        return success

    def delete(self, key: str) -> bool:
        """캐시에서 삭제 (L1 + L2)"""
        l1_deleted = self.l1_cache.delete(key)

        if self.l2_enabled:
            l2_deleted = self._delete_from_l2(key)
            return l1_deleted or l2_deleted

        return l1_deleted

    def clear(self) -> None:
        """전체 캐시 삭제"""
        self.l1_cache.clear()

        if self.l2_enabled:
            for cache_file in self.l2_cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.error(f"Error deleting L2 cache file {cache_file}: {e}")

            logger.info("L2 cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        l1_stats = self.l1_cache.get_stats()

        stats = {
            'l1': {
                'hits': l1_stats.total_hits,
                'misses': l1_stats.total_misses,
                'hit_rate': l1_stats.hit_rate,
                'entries': l1_stats.entry_count,
                'memory_mb': l1_stats.memory_usage_bytes / 1024 / 1024
            }
        }

        if self.l2_enabled:
            l2_files = list(self.l2_cache_dir.glob("*.cache"))
            l2_size = sum(f.stat().st_size for f in l2_files)
            stats['l2'] = {
                'entries': len(l2_files),
                'size_mb': l2_size / 1024 / 1024
            }

        return stats

    def _get_from_l2(self, key: str) -> Optional[Any]:
        """L2 캐시에서 조회"""
        cache_file = self._get_l2_path(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)

            if data.get('expires_at'):
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() >= expires_at:
                    logger.debug(f"L2 cache expired: {key}")
                    cache_file.unlink()
                    return None

            return data.get('value')

        except Exception as e:
            logger.error(f"Error reading L2 cache {key}: {e}")
            return None

    def _set_to_l2(self, key: str, value: Any, ttl_seconds: Optional[int]) -> bool:
        """L2 캐시에 저장"""
        cache_file = self._get_l2_path(key)

        try:
            expires_at = None
            if ttl_seconds and ttl_seconds > 0:
                expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()

            data = {
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at
            }

            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)

            logger.debug(f"L2 cache set: {key}")
            return True

        except Exception as e:
            logger.error(f"Error writing L2 cache {key}: {e}")
            return False

    def _delete_from_l2(self, key: str) -> bool:
        """L2 캐시에서 삭제"""
        cache_file = self._get_l2_path(key)

        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.debug(f"L2 cache deleted: {key}")
                return True
            except Exception as e:
                logger.error(f"Error deleting L2 cache {key}: {e}")

        return False

    def _get_l2_path(self, key: str) -> Path:
        """L2 캐시 파일 경로"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.l2_cache_dir / f"{key_hash}.cache"


def cached(cache: LRUCache, ttl_seconds: int = 300,
          key_func: Optional[Callable] = None):
    캐싱 데코레이터

    Usage:
        @cached(my_cache, ttl_seconds=600)
        def expensive_function(param1, param2):
            ...

        @cached(my_cache, key_func=lambda user_id: f"user_{user_id}")
        def get_user_data(user_id):
            ...
    def decorator(func):
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                args_str = json.dumps([str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())])
                args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
                cache_key = f"{func.__name__}:{args_hash}"

            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            result = func(*args, **kwargs)

            cache.set(cache_key, result, ttl_seconds=ttl_seconds)

            return result

        return wrapper
    return decorator


_price_cache: Optional[MultiLevelCache] = None
_market_data_cache: Optional[MultiLevelCache] = None
_api_cache: Optional[LRUCache] = None


def get_price_cache() -> MultiLevelCache:
    """가격 데이터 캐시"""
    global _price_cache
    if _price_cache is None:
        _price_cache = MultiLevelCache(
            l1_max_size=500,
            l1_max_memory_mb=50,
            l2_enabled=True,
            l2_cache_dir="data/cache/prices"
        )
    return _price_cache


def get_market_data_cache() -> MultiLevelCache:
    """마켓 데이터 캐시"""
    global _market_data_cache
    if _market_data_cache is None:
        _market_data_cache = MultiLevelCache(
            l1_max_size=1000,
            l1_max_memory_mb=100,
            l2_enabled=True,
            l2_cache_dir="data/cache/market"
        )
    return _market_data_cache


def get_api_cache() -> LRUCache:
    """API 응답 캐시"""
    global _api_cache
    if _api_cache is None:
        _api_cache = LRUCache(
            max_size=500,
            max_memory_mb=30,
            default_ttl_seconds=60
        )
    return _api_cache


if __name__ == '__main__':
    print("\n📦 Multi-Level Cache Test")
    print("=" * 60)

    cache = MultiLevelCache(l1_max_size=10, l1_max_memory_mb=1)

    print("\n[Test 1] Set and Get")
    cache.set("test_key", {"price": 73500, "volume": 1000000}, ttl_seconds=60)
    value = cache.get("test_key")
    print(f"✓ Retrieved: {value}")

    print("\n[Test 2] Cache Statistics")
    stats = cache.get_stats()
    print(f"✓ L1 Hit Rate: {stats['l1']['hit_rate']:.1%}")
    print(f"✓ L1 Entries: {stats['l1']['entries']}")
    print(f"✓ L1 Memory: {stats['l1']['memory_mb']:.2f}MB")

    print("\n[Test 3] Cached Decorator")

    test_cache = LRUCache(max_size=10, max_memory_mb=1)

    @cached(test_cache, ttl_seconds=300)
    def expensive_calculation(n):
        """Simulate expensive operation"""
        return sum(range(n))

    result1 = expensive_calculation(1000)
    result2 = expensive_calculation(1000)
    print(f"✓ Results: {result1} == {result2}")

    print("\n[OK] Cache tests complete!")
