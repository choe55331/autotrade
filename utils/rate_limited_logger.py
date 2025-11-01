"""
AutoTrade Pro - Rate-Limited Logger
고빈도 로깅으로 인한 성능 저하 방지
"""
import time
import logging
from typing import Dict, Optional
from functools import wraps
from collections import defaultdict


class RateLimitedLogger:
    """
    Rate-Limited Logger

    특징:
    - 동일한 메시지를 일정 시간 내에 한 번만 로깅
    - 키 기반 rate limiting (예: stock_code별로 제한)
    - 스킵된 로그 카운팅
    """

    def __init__(
        self,
        logger: logging.Logger,
        rate_limit_seconds: float = 1.0,
        count_skipped: bool = True
    ):
        """
        Args:
            logger: 원본 로거
            rate_limit_seconds: Rate limit 시간 (초)
            count_skipped: 스킵된 로그 카운팅 여부
        """
        self.logger = logger
        self.rate_limit = rate_limit_seconds
        self.count_skipped = count_skipped

        # 마지막 로그 시간 추적
        self.last_log_time: Dict[str, float] = {}

        # 스킵 카운터
        self.skip_counter: Dict[str, int] = defaultdict(int)

    def _should_log(self, key: str) -> bool:
        """로그 가능 여부 확인"""
        now = time.time()
        last_time = self.last_log_time.get(key, 0)

        if now - last_time >= self.rate_limit:
            self.last_log_time[key] = now
            return True
        else:
            if self.count_skipped:
                self.skip_counter[key] += 1
            return False

    def debug(self, key: str, message: str, *args, **kwargs):
        """Rate-limited debug 로그"""
        if self._should_log(key):
            skipped = self.skip_counter.get(key, 0)
            if skipped > 0:
                message = f"{message} (스킵된 로그: {skipped}개)"
                self.skip_counter[key] = 0

            self.logger.debug(message, *args, **kwargs)

    def info(self, key: str, message: str, *args, **kwargs):
        """Rate-limited info 로그"""
        if self._should_log(key):
            skipped = self.skip_counter.get(key, 0)
            if skipped > 0:
                message = f"{message} (스킵된 로그: {skipped}개)"
                self.skip_counter[key] = 0

            self.logger.info(message, *args, **kwargs)

    def warning(self, key: str, message: str, *args, **kwargs):
        """Rate-limited warning 로그"""
        if self._should_log(key):
            skipped = self.skip_counter.get(key, 0)
            if skipped > 0:
                message = f"{message} (스킵된 로그: {skipped}개)"
                self.skip_counter[key] = 0

            self.logger.warning(message, *args, **kwargs)

    def error(self, key: str, message: str, *args, **kwargs):
        """Rate-limited error 로그 (rate limit 더 짧게)"""
        # 에러는 더 자주 로깅 (rate_limit / 10)
        now = time.time()
        last_time = self.last_log_time.get(f"error_{key}", 0)

        if now - last_time >= (self.rate_limit / 10):
            self.last_log_time[f"error_{key}"] = now
            self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Critical 로그 (항상 로깅, rate limit 없음)"""
        self.logger.critical(message, *args, **kwargs)

    def reset_stats(self):
        """통계 초기화"""
        self.last_log_time.clear()
        self.skip_counter.clear()

    def get_stats(self) -> Dict[str, int]:
        """스킵 통계 반환"""
        return dict(self.skip_counter)


def rate_limit_log(rate_limit_seconds: float = 1.0):
    """
    함수 데코레이터: 함수 내부 로깅을 rate limit

    Usage:
        @rate_limit_log(rate_limit_seconds=5.0)
        def my_function():
            logger.info("This will be rate limited")
    """
    def decorator(func):
        last_log = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            func_name = func.__name__

            if now - last_log.get(func_name, 0) >= rate_limit_seconds:
                last_log[func_name] = now
                return func(*args, **kwargs)

        return wrapper
    return decorator


class LogThrottler:
    """
    로그 스로틀링: 일정 시간 동안 최대 N개만 로깅

    예: 1초에 최대 10개 로그만 허용
    """

    def __init__(
        self,
        logger: logging.Logger,
        max_logs_per_period: int = 10,
        period_seconds: float = 1.0
    ):
        self.logger = logger
        self.max_logs = max_logs_per_period
        self.period = period_seconds

        self.log_timestamps: list[float] = []

    def _can_log(self) -> bool:
        """로그 가능 여부 확인"""
        now = time.time()

        # 만료된 타임스탬프 제거
        self.log_timestamps = [
            ts for ts in self.log_timestamps
            if now - ts < self.period
        ]

        if len(self.log_timestamps) < self.max_logs:
            self.log_timestamps.append(now)
            return True

        return False

    def info(self, message: str, *args, **kwargs):
        """Throttled info 로그"""
        if self._can_log():
            self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Throttled warning 로그"""
        if self._can_log():
            self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Throttled error 로그"""
        if self._can_log():
            self.logger.error(message, *args, **kwargs)


class AggregatedLogger:
    """
    집계 로거: 동일한 로그를 모아서 주기적으로 요약 로깅

    예: "가격 업데이트" 로그를 100개 모아서 한 번에 로깅
    """

    def __init__(
        self,
        logger: logging.Logger,
        aggregate_count: int = 100,
        flush_interval_seconds: float = 10.0
    ):
        self.logger = logger
        self.aggregate_count = aggregate_count
        self.flush_interval = flush_interval_seconds

        self.message_buffer: Dict[str, list] = defaultdict(list)
        self.last_flush_time: Dict[str, float] = {}

    def add(self, key: str, message: str):
        """로그 메시지 추가 (즉시 로깅하지 않음)"""
        self.message_buffer[key].append((time.time(), message))

        # 버퍼가 가득 차거나 시간이 지나면 flush
        if len(self.message_buffer[key]) >= self.aggregate_count:
            self.flush(key)
        elif time.time() - self.last_flush_time.get(key, 0) >= self.flush_interval:
            self.flush(key)

    def flush(self, key: Optional[str] = None):
        """버퍼 flush (집계 로깅)"""
        if key:
            keys = [key]
        else:
            keys = list(self.message_buffer.keys())

        for k in keys:
            if not self.message_buffer[k]:
                continue

            count = len(self.message_buffer[k])
            first_msg = self.message_buffer[k][0][1]
            last_msg = self.message_buffer[k][-1][1]

            summary = f"[{k}] 집계 로그 {count}개: 첫 메시지='{first_msg}' | 마지막='{last_msg}'"
            self.logger.info(summary)

            self.message_buffer[k].clear()
            self.last_flush_time[k] = time.time()

    def __del__(self):
        """소멸자: 남은 버퍼 flush"""
        self.flush()


# 편의 함수
def get_rate_limited_logger(
    logger_name: str = __name__,
    rate_limit_seconds: float = 1.0
) -> RateLimitedLogger:
    """Rate-limited logger 생성"""
    base_logger = logging.getLogger(logger_name)
    return RateLimitedLogger(base_logger, rate_limit_seconds)


def get_log_throttler(
    logger_name: str = __name__,
    max_logs_per_period: int = 10,
    period_seconds: float = 1.0
) -> LogThrottler:
    """Log throttler 생성"""
    base_logger = logging.getLogger(logger_name)
    return LogThrottler(base_logger, max_logs_per_period, period_seconds)


def get_aggregated_logger(
    logger_name: str = __name__,
    aggregate_count: int = 100,
    flush_interval_seconds: float = 10.0
) -> AggregatedLogger:
    """Aggregated logger 생성"""
    base_logger = logging.getLogger(logger_name)
    return AggregatedLogger(base_logger, aggregate_count, flush_interval_seconds)
