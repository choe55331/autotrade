"""
API Response Caching Layer v1.0
Flask route 응답 캐싱 시스템
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import hashlib
import json
from typing import Any, Callable, Optional


class SimpleCache:
    """간단한 메모리 기반 캐시"""

    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._hit_count = 0
        self._miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        if key in self._cache:
            self._hit_count += 1
            return self._cache[key]
        self._miss_count += 1
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """캐시에 값 저장 (TTL: seconds)"""
        self._cache[key] = value
        self._timestamps[key] = datetime.now() + timedelta(seconds=ttl)

    def is_expired(self, key: str) -> bool:
        """캐시 만료 확인"""
        if key not in self._timestamps:
            return True
        return datetime.now() > self._timestamps[key]

    def invalidate(self, key: str):
        """특정 키 무효화"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]

    def clear(self):
        """전체 캐시 클리어"""
        self._cache.clear()
        self._timestamps.clear()

    def cleanup_expired(self):
        """만료된 캐시 항목 정리"""
        expired_keys = [
            key for key in self._cache.keys()
            if self.is_expired(key)
        ]
        for key in expired_keys:
            self.invalidate(key)

    def get_stats(self) -> dict:
        """캐시 통계"""
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0

        return {
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_items': len(self._cache),
            'cache_size_kb': self._estimate_size()
        }

    def _estimate_size(self) -> float:
        """캐시 크기 추정 (KB)"""
        try:
            size_bytes = sum(
                len(str(v).encode('utf-8'))
                for v in self._cache.values()
            )
            return round(size_bytes / 1024, 2)
        except:
            return 0.0


_cache_instance = SimpleCache()


def get_cache() -> SimpleCache:
    """캐시 싱글톤 인스턴스 반환"""
    return _cache_instance


def cache_key_from_request(prefix: str = '') -> str:
    """요청으로부터 캐시 키 생성"""
    key_parts = [
        prefix,
        request.path,
        request.method,
        str(sorted(request.args.items())),
    ]

    key_string = '|'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ''):
    """
    Flask route 캐싱 데코레이터

    Args:
    """
        ttl: Time to live in seconds (default: 300 = 5분)
        key_prefix: 캐시 키 접두사

    Usage:
        @app.route('/api/data')
        @cached(ttl=60, key_prefix='api_data')
        def get_data():
            return jsonify({'data': expensive_operation()})
    """
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache = get_cache()

            cache_key = cache_key_from_request(prefix=key_prefix or f.__name__)

            cached_response = cache.get(cache_key)
            if cached_response is not None and not cache.is_expired(cache_key):
                if isinstance(cached_response, tuple):
                    response, status_code = cached_response
                    return response, status_code
                return cached_response

            response = f(*args, **kwargs)

            if isinstance(response, tuple):
                cache.set(cache_key, response, ttl)
            else:
                cache.set(cache_key, response, ttl)

            return response

        return decorated_function
    return decorator


def cache_json(ttl: int = 300, key_prefix: str = ''):
    """
    JSON 응답 전용 캐싱 데코레이터

    Args:
        ttl: Time to live in seconds
        key_prefix: 캐시 키 접두사

    Usage:
        @app.route('/api/portfolio')
        """
        @cache_json(ttl=30, key_prefix='portfolio')
        def get_portfolio():
            return {'positions': get_positions()}
    """
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache = get_cache()

            cache_key = cache_key_from_request(prefix=key_prefix or f.__name__)

            cached_data = cache.get(cache_key)
            if cached_data is not None and not cache.is_expired(cache_key):
                return jsonify(cached_data)

            result = f(*args, **kwargs)

            if hasattr(result, 'get_json'):
                data = result.get_json()
            elif isinstance(result, dict):
                data = result
            else:
                return result

            cache.set(cache_key, data, ttl)

            return jsonify(data)

        return decorated_function
    return decorator


def invalidate_cache(key_prefix: str = ''):
    """
    특정 접두사를 가진 캐시 무효화

    Args:
        key_prefix: 무효화할 캐시 키 접두사
    """
    cache = get_cache()

    if key_prefix:
        keys_to_invalidate = [
            key for key in cache._cache.keys()
            if key.startswith(key_prefix)
        ]
        for key in keys_to_invalidate:
            cache.invalidate(key)
    else:
        cache.clear()


def cleanup_cache():
    """만료된 캐시 정리 (백그라운드 작업용)"""
    cache = get_cache()
    cache.cleanup_expired()


def get_cache_stats() -> dict:
    """캐시 통계 반환"""
    cache = get_cache()
    return cache.get_stats()


class CacheWarmer:
    """캐시 워머 - 자주 사용되는 데이터 미리 로드"""

    def __init__(self):
        self.warmup_urls = []

    def add_warmup_url(self, url: str, ttl: int = 300):
        """워밍업 대상 URL 추가"""
        self.warmup_urls.append({'url': url, 'ttl': ttl})

    def warmup(self, client):
        """캐시 워밍업 실행"""
        for item in self.warmup_urls:
            try:
                with client.get(item['url']) as response:
                    if response.status_code == 200:
                        print(f"✓ Warmed up: {item['url']}")
            except Exception as e:
                print(f"✗ Failed to warm up {item['url']}: {e}")


_cache_warmer = CacheWarmer()


def get_cache_warmer() -> CacheWarmer:
    """캐시 워머 싱글톤 반환"""
    return _cache_warmer


__all__ = [
    'SimpleCache',
    'get_cache',
    'cached',
    'cache_json',
    'cache_key_from_request',
    'invalidate_cache',
    'cleanup_cache',
    'get_cache_stats',
    'CacheWarmer',
    'get_cache_warmer'
]
